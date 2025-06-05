# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from .models import LiveWin, Offer, PaymentMethod, SocialLink, ContactMessage, PageVisit, UserInteraction


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
    list_display = ['title', 'scheduled_start', 'duration_hours', 'active_status_display', 'time_remaining', 'action_buttons']
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


@admin.register(PaymentMethod)
class PaymentMethodAdmin(BaseModelAdmin):
    list_display = ['name', 'is_active', 'order', 'status_indicator', 'action_buttons']
    list_editable = ['is_active', 'order']
    ordering = ['order']
    search_fields = ['name']
    list_per_page = 5

    def status_indicator(self, obj):
        color = 'green' if obj.is_active else 'gray'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    status_indicator.short_description = 'Status'

    def action_buttons(self, obj):
        return format_html(
            '<div class="action-buttons">{}</div>',
            self.edit_button(obj) + self.delete_button(obj))

    action_buttons.short_description = 'Actions'


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
    list_display = ('path', 'ip_address', 'country', 'timestamp', 'view_button')
    list_filter = ('path', 'country', 'timestamp')
    search_fields = ('path', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('path', 'ip_address', 'country', 'timestamp')
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
@staff_member_required
def analytics_dashboard(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timezone.timedelta(days=1)

    visits_today = PageVisit.objects.filter(timestamp__gte=today_start).count()
    visits_yesterday = PageVisit.objects.filter(timestamp__gte=yesterday_start, timestamp__lt=today_start).count()
    total_visits = PageVisit.objects.count()

    interactions_today = UserInteraction.objects.filter(timestamp__gte=today_start).count()
    popular_interactions = UserInteraction.objects.values('type').annotate(count=Count('id')).order_by('-count')[:5]

    offer_interests = UserInteraction.objects.filter(type='offer_interest').values(
        'additional_data__offer_id'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    offer_ids = []
    for item in offer_interests:
        offer_id = item['additional_data__offer_id']
        if offer_id and str(offer_id).isdigit():
            offer_ids.append(int(offer_id))

    offers = Offer.objects.filter(id__in=offer_ids).in_bulk()

    for interest in offer_interests:
        offer_id = interest['additional_data__offer_id']
        try:
            interest['title'] = offers.get(int(offer_id)).title if int(offer_id) in offers else 'Unknown Offer'
        except (TypeError, ValueError, KeyError):
            interest['title'] = 'Unknown Offer'

    popular_pages = PageVisit.objects.values('path').annotate(visits=Count('id')).order_by('-visits')[:10]

    context = {
        'visits_today': visits_today,
        'visits_yesterday': visits_yesterday,
        'visit_change': ((visits_today - visits_yesterday) / visits_yesterday * 100) if visits_yesterday else 0,
        'total_visits': total_visits,
        'interactions_today': interactions_today,
        'popular_interactions': popular_interactions,
        'offer_interests': offer_interests,
        'popular_pages': popular_pages,
    }
    return render(request, 'admin/analytics_dashboard.html', context)


# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Administration Portal'
    index_title = 'Dashboard Overview'

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path('analytics/', self.admin_view(analytics_dashboard), name='analytics_dashboard'),
        ]
        return urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_analytics_link'] = True
        return super().index(request, extra_context)


custom_admin_site = CustomAdminSite(name='myadmin')

# Re-register all models with custom admin site
models = [LiveWin, Offer, PaymentMethod, SocialLink, ContactMessage, PageVisit, UserInteraction]
for model in models:
    try:
        custom_admin_site.register(model, globals()[f"{model.__name__}Admin"])
    except:
        custom_admin_site.register(model)
