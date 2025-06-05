
# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from .models import LiveWin, Offer, PaymentMethod, SocialLink, ContactMessage, PageVisit, UserInteraction


class CustomAdminSite(admin.AdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Administration Portal'
    index_title = 'Dashboard Overview'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        urls += [
            path('analytics/', self.admin_view(analytics_dashboard)),
        ]
        return urls


custom_admin_site = CustomAdminSite(name='myadmin')


class BaseModelAdmin(admin.ModelAdmin):
    def edit_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html('<a class="button" href="{}">Edit</a>', url)

    def delete_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_delete', args=[obj.id])
        return format_html('<a class="button delete-button" href="{}">Delete</a>', url)

    edit_button.short_description = 'Edit'
    delete_button.short_description = 'Delete'


@admin.register(LiveWin, site=custom_admin_site)
class LiveWinAdmin(BaseModelAdmin):
    list_display = ['username', 'amount', 'timestamp', 'status_indicator', 'edit_button', 'delete_button']
    list_editable = ['amount']
    search_fields = ['username']
    list_filter = ['timestamp']
    ordering = ['-timestamp']

    def status_indicator(self, obj):
        color = 'green' if obj.visible else 'gray'
        text = 'Visible' if obj.visible else 'Hidden'
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    status_indicator.short_description = 'Status'


@admin.register(Offer, site=custom_admin_site)
class OfferAdmin(BaseModelAdmin):
    list_display = ['title', 'scheduled_start', 'duration_hours', 'active_status_display', 'time_remaining',
                    'edit_button', 'delete_button']
    list_editable = ['scheduled_start', 'duration_hours']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['-scheduled_start']

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


@admin.register(PaymentMethod, site=custom_admin_site)
class PaymentMethodAdmin(BaseModelAdmin):
    list_display = ['name', 'is_active', 'order', 'status_indicator', 'edit_button', 'delete_button']
    list_editable = ['is_active', 'order']
    ordering = ['order']
    search_fields = ['name']

    def status_indicator(self, obj):
        color = 'green' if obj.is_active else 'gray'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    status_indicator.short_description = 'Status'


@admin.register(SocialLink, site=custom_admin_site)
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


@admin.register(ContactMessage, site=custom_admin_site)
class ContactMessageAdmin(BaseModelAdmin):
    list_display = ['name', 'email', 'timestamp', 'processed_status', 'edit_button', 'delete_button']
    list_filter = ['is_processed', 'timestamp']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_processed']
    ordering = ['-timestamp']

    def processed_status(self, obj):
        color = 'green' if obj.is_processed else 'orange'
        text = 'Processed' if obj.is_processed else 'Pending'
        return format_html(f'<span class="status-indicator" style="background-color: {color}"></span> {text}')

    processed_status.short_description = 'Status'


@admin.register(PageVisit, site=custom_admin_site)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'ip_address', 'country', 'timestamp', 'view_button')
    list_filter = ('path', 'country', 'timestamp')
    search_fields = ('path', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('path', 'ip_address', 'country', 'timestamp')

    def view_button(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html('<a class="button" href="{}">View</a>', url)

    view_button.short_description = 'Actions'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserInteraction, site=custom_admin_site)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('type', 'element_id', 'page_path', 'offer_id', 'timestamp', 'view_button')
    list_filter = ('type', 'page_path', 'timestamp')
    search_fields = ('element_id', 'page_path')
    date_hierarchy = 'timestamp'
    readonly_fields = ('type', 'element_id', 'page_path', 'additional_data', 'timestamp')

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


# Add CSS to admin interface
class Media:
    css = {
        'all': ('admin/css/custom.css',)
    }


# Analytics Dashboard
@staff_member_required
def analytics_dashboard(request):
    # Time calculations
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timezone.timedelta(days=1)

    # Visit statistics
    visits_today = PageVisit.objects.filter(timestamp__gte=today_start).count()
    visits_yesterday = PageVisit.objects.filter(
        timestamp__gte=yesterday_start,
        timestamp__lt=today_start
    ).count()
    total_visits = PageVisit.objects.count()

    # Interaction statistics
    interactions_today = UserInteraction.objects.filter(timestamp__gte=today_start).count()
    popular_interactions = UserInteraction.objects.values('type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Offer interest
    offer_interests = UserInteraction.objects.filter(type='offer_interest').values(
        'additional_data__offer_id'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Map offer IDs to offer titles
    offer_ids = [item['additional_data__offer_id'] for item in offer_interests]
    offers = Offer.objects.filter(id__in=offer_ids).in_bulk()

    # Add titles to interests
    for interest in offer_interests:
        offer_id = interest['additional_data__offer_id']
        interest['title'] = offers.get(int(offer_id)).title if offer_id.isdigit() and int(
            offer_id) in offers else 'Unknown Offer'

    # Popular pages
    popular_pages = PageVisit.objects.values('path').annotate(
        visits=Count('id')
    ).order_by('-visits')[:10]

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


# Add link to admin index
class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_analytics_link'] = True
        return super().index(request, extra_context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        urls += [
            path('analytics/', self.admin_view(analytics_dashboard), name='analytics_dashboard'),
        ]
        return urls


# Replace default admin site
custom_admin_site = CustomAdminSite(name='myadmin')


# Register all models with the custom admin site
# (You'll need to re-register all your existing models here)
@admin.register(LiveWin)
class LiveWinAdmin(admin.ModelAdmin):
    list_display = ['username', 'amount', 'timestamp']
    list_editable = ['amount']
    search_fields = ['username']
    list_filter = ['timestamp']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_start', 'duration_hours', 'countdown_end', 'active_status_display']
    list_editable = ['scheduled_start', 'duration_hours']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['-scheduled_start']

    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Timing', {
            'fields': ('scheduled_start', 'duration_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    @admin.display(description='Active', ordering='is_active')
    def active_status_display(self, obj):
        color = 'green' if obj.is_active else 'red'
        status = "✔ Active" if obj.is_active else "✖ Inactive"
        return format_html(f'<b style="color: {color};">{status}</b>')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    ordering = ['order']
    search_fields = ['name']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SocialLink.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'timestamp', 'is_processed']
    list_filter = ['is_processed', 'timestamp']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_processed']
    ordering = ['-timestamp']


# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import PageVisit, UserInteraction


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'ip_address', 'country', 'timestamp')
    list_filter = ('path', 'country', 'timestamp')
    search_fields = ('path', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('path', 'ip_address', 'country', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('type', 'element_id', 'page_path', 'offer_id', 'timestamp')
    list_filter = ('type', 'page_path', 'timestamp')
    search_fields = ('element_id', 'page_path')
    date_hierarchy = 'timestamp'
    readonly_fields = ('type', 'element_id', 'page_path', 'additional_data', 'timestamp')

    def offer_id(self, obj):
        if obj.type == 'offer_interest':
            return obj.additional_data.get('offer_id', 'N/A')
        return '-'

    offer_id.short_description = 'Offer ID'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False