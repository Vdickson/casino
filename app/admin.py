# casino/admin.py
from django.contrib import admin
from .models import *

@admin.register(LiveWin)
class LiveWinAdmin(admin.ModelAdmin):
    list_display = ['username', 'amount', 'timestamp']
    list_editable = ['amount']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_start', 'duration_hours', 'countdown_end', 'is_active']
    list_editable = ['scheduled_start', 'duration_hours']
    list_filter = ['is_active']

    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Timing', {
            'fields': ('scheduled_start', 'duration_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SocialLink.objects.exists()

from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'timestamp', 'is_processed']
    list_filter = ['is_processed']
    search_fields = ['name', 'email']
    list_editable = ['is_processed']