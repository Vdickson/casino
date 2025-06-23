# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, F, Q
from django.db.models.functions import TruncDay
from django.views.decorators.cache import cache_page

from . import views
from .models import LiveWin, Offer, PaymentMethod, SocialLink, ContactMessage, PageVisit, UserInteraction, Testimonial, \
    CookieConsent, AnalyticsEvent, RechargeRequest


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 10

    def edit_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html('<a class="button" href="{}">Edit</a>', url)

    def delete_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_delete', args=[obj.id])
        return format_html('<a class="button delete-button" href="{}">Delete</a>', url)

    edit_button.short_description = ''
    delete_button.short_description = ''

    class Media:
        css = {'all': ('admin/css/custom.css',)}


@admin.register(LiveWin)
class LiveWinAdmin(BaseModelAdmin):
    list_display = ['username', 'amount', 'timestamp', 'status_indicator', 'action_buttons']
    list_editable = ['amount']
    search_fields = ['username']
    list_filter = ['timestamp']
    ordering = ['-timestamp']
    list_per_page = 10

    def status_indicator(self, obj):
        color = 'green' if obj.visible else 'gray'
        text = 'Visible' if obj.visible else 'Hidden'
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    status_indicator.short_description = 'Status'

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'


@admin.register(Offer)
class OfferAdmin(BaseModelAdmin):
    list_display = ['title', 'scheduled_start', 'duration_hours', 'active_status_display', 'time_remaining',
                    'action_buttons']
    list_editable = ['scheduled_start', 'duration_hours']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['-scheduled_start']
    list_per_page = 10

    @admin.display(description='Status')
    def active_status_display(self, obj):
        color = 'green' if obj.is_active else 'red'
        status = "Active" if obj.is_active else "Inactive"
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {status}')

    @admin.display(description='Time Remaining')
    def time_remaining(self, obj):
        if obj.time_remaining:
            hours, remainder = divmod(obj.time_remaining.seconds, 3600)
            minutes = remainder // 60
            return f"{hours}h {minutes}m"
        return "N/A"

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'


# models.py - Keep this version and remove the simpler one
# class PaymentMethod(models.Model):
#     PAYMENT_TYPES = (
#         ('cashapp', 'CashApp'),
#         ('bitcoin', 'Bitcoin'),
#         ('venmo', 'Venmo'),
#         ('paypal', 'PayPal'),
#         ('chime', 'Chime'),
#         ('other', 'Other'),
#     )
#
#     class PaymentMethod(models.Model):
#         PAYMENT_TYPES = (
#             ('cashapp', 'CashApp'),
#             ('bitcoin', 'Bitcoin'),
#             ('venmo', 'Venmo'),
#             ('paypal', 'PayPal'),
#             ('chime', 'Chime'),
#             ('other', 'Other'),
#         )
#
#         # Add default='other' to handle existing records
#         type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='other')
#         # ... rest of your fields ...
#
#     name = models.CharField(max_length=50)
#     type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
#     logo = models.ImageField(upload_to='payments/')
#     is_active = models.BooleanField(default=True)
#     order = models.PositiveIntegerField(default=0)
#     account_id = models.CharField(max_length=100, blank=True,
#                                 help_text="Your account ID/address for this payment method")
#     qr_code = models.ImageField(upload_to='payments/qr_codes/', blank=True, null=True)
#     instructions = models.TextField(blank=True, help_text="Special instructions for this payment method")
#     min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
#     max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
#
#     def __str__(self):
#         return f"{self.get_type_display()} - {self.name}"
#
#     class Meta:
#         ordering = ['order']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['facebook', 'whatsapp', 'telegram', 'edit_button']

    def edit_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html('<a class="button" href="{}">Edit</a>', url)

    edit_button.short_description = 'Actions'

    def has_add_permission(self, request):
        return not SocialLink.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {'all': ('admin/css/custom.css',)}


@admin.register(ContactMessage)
class ContactMessageAdmin(BaseModelAdmin):
    list_display = ['name', 'email', 'timestamp', 'is_processed', 'processed_status', 'action_buttons']
    list_editable = ['is_processed']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_processed']
    ordering = ['-timestamp']
    list_per_page = 10

    def processed_status(self, obj):
        color = 'green' if obj.is_processed else 'orange'
        text = 'Processed' if obj.is_processed else 'Pending'
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    processed_status.short_description = 'Status'

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'country', 'timestamp', 'duration', 'last_activity', 'view_button')
    list_filter = ('country', 'timestamp', 'is_active')
    list_filter = ('country',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('ip_address', 'country', 'timestamp', 'duration', 'session_key')
    list_per_page = 15

    def view_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html('<a class="button" href="{}">View</a>', url)

    view_button.short_description = 'Actions'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    class Media:
        css = {'all': ('admin/css/custom.css',)}


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('type', 'element_id', 'page_path', 'offer_id', 'timestamp', 'view_button')
    list_filter = ('type', 'page_path', 'timestamp')
    search_fields = ('element_id', 'page_path')
    date_hierarchy = 'timestamp'
    readonly_fields = ('type', 'element_id', 'page_path', 'additional_data', 'timestamp')
    list_per_page = 15

    def offer_id(self, obj):
        return obj.additional_data.get('offer_id', 'N/A') if obj.type == 'offer_interest' else '-'

    offer_id.short_description = 'Offer ID'

    def view_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html('<a class="button" href="{}">View</a>', url)

    view_button.short_description = 'Actions'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    class Media:
        css = {'all': ('admin/css/custom.css',)}


# Analytics Dashboard


# Custom Admin Site
# admin.py
class CustomAdminSite(admin.AdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Administration Portal'
    index_title = 'Dashboard Overview'

    def get_urls(self):
        urls = super().get_urls()
        # Remove the catch-all pattern
        catch_all_pattern = urls.pop()

        # Add analytics route before the catch-all pattern
        urls += [
            # path('analytics/', self.admin_view(analytics_dashboard), name='analytics_dashboard'),
            path('analytics/', self.admin_view(views.analytics_dashboard), name='analytics_dashboard'),
            catch_all_pattern  # Re-add the catch-all pattern last
        ]

        return urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_analytics_link'] = True
        return super().index(request, extra_context)

    # NEW: Add this method to customize the app list
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)

        # Add custom analytics link to the app list
        analytics_link = {
            'name': 'Analytics Dashboard',
            'app_label': 'analytics',
            'models': [
                {
                    'name': 'View Analytics',
                    'object_name': 'analytics',
                    'admin_url': reverse('admin:analytics_dashboard'),
                    'view_only': True,
                }
            ]
        }

        app_list.insert(0, analytics_link)

        return app_list


@admin.register(Testimonial)
class TestimonialAdmin(BaseModelAdmin):
    list_display = ['name', 'content_preview', 'created_at', 'is_approved', 'action_buttons']
    list_editable = ['is_approved']
    search_fields = ['name', 'content']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Content'

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'


# ===== NEW MODELS FOR COOKIES & ANALYTICS =====
@admin.register(CookieConsent)
class CookieConsentAdmin(BaseModelAdmin):
    list_display = ['session_key', 'analytics_status', 'marketing_status', 'timestamp', 'action_buttons']
    list_filter = ['analytics', 'marketing', 'timestamp']
    search_fields = ['session_key']
    ordering = ['-timestamp']
    list_per_page = 20
    readonly_fields = ['session_key', 'timestamp']

    @admin.display(description='Analytics')
    def analytics_status(self, obj):
        color = 'green' if obj.analytics else 'red'
        text = "Enabled" if obj.analytics else "Disabled"
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    @admin.display(description='Marketing')
    def marketing_status(self, obj):
        color = 'green' if obj.marketing else 'red'
        text = "Enabled" if obj.marketing else "Disabled"
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'


@admin.register(RechargeRequest)
class RechargeRequestAdmin(BaseModelAdmin):
    list_display = ['id', 'player', 'payment_method', 'amount', 'status', 'created_at', 'action_buttons']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['player__username', 'transaction_id']
    readonly_fields = ['player', 'payment_method', 'amount', 'transaction_id', 'screenshot', 'created_at']
    list_editable = ['status']

    def process_recharge(self, request, queryset):
        queryset.update(status='completed', processed_at=timezone.now())
        self.message_user(request, f"Marked {queryset.count()} recharges as completed")

    process_recharge.short_description = "Mark selected as completed"

    actions = [process_recharge]

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'



@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['event_summary', 'session_key', 'path', 'timestamp', 'user_insights']
    list_filter = ['category', 'action', 'timestamp']
    search_fields = ['label', 'path', 'session_key']
    date_hierarchy = 'timestamp'
    list_per_page = 25
    readonly_fields = ['session_key', 'category', 'action', 'label', 'path', 'value', 'timestamp']

    @admin.display(description='Event')
    def event_summary(self, obj):
        return f"{obj.category} / {obj.action}"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Top events
        top_events = AnalyticsEvent.objects.values(
            'category', 'action'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Daily event counts
        daily_counts = AnalyticsEvent.objects.annotate(
            date=TruncDay('timestamp')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:30]

        # Top pages
        top_pages = AnalyticsEvent.objects.values(
            'path'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Consent stats
        consent_stats = CookieConsent.objects.aggregate(
            total=Count('id'),
            analytics=Count('id', filter=Q(analytics=True)),
            marketing=Count('id', filter=Q(marketing=True)))

        extra_context.update({
            'top_events': top_events,
            'daily_counts': list(daily_counts),
            'top_pages': top_pages,
            'consent_stats': consent_stats,
        })

        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description='User Insights')
    def user_insights(self, obj):
        try:
            consent = CookieConsent.objects.get(session_key=obj.session_key)
            insights = []
            if consent.analytics:
                insights.append("Analytics")
            if consent.marketing:
                insights.append("Marketing")
            return ", ".join(insights) or "None"
        except CookieConsent.DoesNotExist:
            return "No consent"


custom_admin_site = CustomAdminSite(name='admin')
# Register models with admin classes
custom_admin_site.register(CookieConsent, CookieConsentAdmin)
custom_admin_site.register(AnalyticsEvent, AnalyticsEventAdmin)

from django.contrib.admin.sites import AlreadyRegistered

# Re-register all models with custom admin site
models = [LiveWin, Offer, PaymentMethod, SocialLink, ContactMessage, PageVisit, AnalyticsEvent, Testimonial,
          CookieConsent, UserInteraction, RechargeRequest, ]

for model in models:
    try:
        custom_admin_site.register(model, globals()[f"{model.__name__}Admin"])
    except AlreadyRegistered:
        pass
    except KeyError:
        # If no custom ModelAdmin class is defined, register model without admin class
        try:
            custom_admin_site.register(model)
        except AlreadyRegistered:
            pass
