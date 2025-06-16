# models.py
from django.db import models
from django.utils import timezone
from django.core.cache import cache

from django.core.exceptions import ValidationError


class LiveWin(models.Model):
    username = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    visible = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index

    class Meta:
        indexes = [
            models.Index(fields=['-timestamp'], name='livewin_timestamp_idx'),
            models.Index(fields=['visible'], name='livewin_visible_idx'),
        ]


class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_start = models.DateTimeField(db_index=True)  # Added index
    duration_hours = models.PositiveIntegerField(default=24)
    countdown_end = models.DateTimeField(blank=True, null=True, db_index=True)  # Added index
    is_active = models.BooleanField(default=True)  # ✅ Add this line

    def save(self, *args, **kwargs):
        if self.scheduled_start and self.duration_hours:
            self.countdown_end = self.scheduled_start + timezone.timedelta(hours=self.duration_hours)
        super().save(*args, **kwargs)
        cache.delete('offers_cache')  # Clear offers cache

    def delete(self, *args, **kwargs):
        cache.delete('offers_cache')
        super().delete(*args, **kwargs)

    @property
    def time_until_start(self):
        now = timezone.now()
        return (self.scheduled_start - now) if now < self.scheduled_start else None

    @property
    def time_remaining(self):
        now = timezone.now()
        if self.countdown_end and self.scheduled_start <= now <= self.countdown_end:
            return self.countdown_end - now
        return None

    def clean(self):
        if not (self.scheduled_start and self.countdown_end):
            return

        overlapping = Offer.objects.filter(
            models.Q(scheduled_start__lt=self.countdown_end) &
            models.Q(countdown_end__gt=self.scheduled_start)
        ).exclude(pk=self.pk).exists()

        if overlapping:
            raise ValidationError("Offers cannot overlap in time")

    class Meta:
        indexes = [
            models.Index(fields=['scheduled_start', 'countdown_end']),
            models.Index(fields=['is_active', 'scheduled_start']),
            models.Index(fields=['is_active', 'countdown_end']),
        ]


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='payments/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('payment_methods_cache')  # Clear cache on save

    def delete(self, *args, **kwargs):
        cache.delete('payment_methods_cache')  # Clear cache on delete
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['order']


class SocialLink(models.Model):
    facebook = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    telegram = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('social_link_cache')

    def delete(self, *args, **kwargs):
        cache.delete('social_link_cache')
        super().delete(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)


class PageVisit(models.Model):
    ip_address = models.CharField(max_length=45, default='Unknown')
    country = models.CharField(max_length=100, default='Unknown')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity = models.DateTimeField(auto_now=True)  # Track last update
    duration = models.PositiveIntegerField(default=0)  # Total active seconds
    session_key = models.CharField(max_length=40, unique=True)
    path = models.CharField(max_length=255, default='/')  # Add this new field


    def __str__(self):
        return f"{self.ip_address} ({self.country}) - {self.duration}s - {self.path}"

    class Meta:
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['session_key']),
        ]


class UserInteraction(models.Model):
    INTERACTION_TYPES = (
        ('button_click', 'Button Click'),
        ('form_submit', 'Form Submission'),
        ('link_click', 'Link Click'),
        ('offer_interest', 'Offer Interest'),
        ('payment_click', 'Payment Method Click'),
    )
    page_visit = models.ForeignKey('PageVisit', on_delete=models.SET_NULL, null=True, blank=True, related_name='interactions')
    type = models.CharField(max_length=50, choices=INTERACTION_TYPES)
    element_id = models.CharField(max_length=100, blank=True, null=True)
    page_path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    additional_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_display()} on {self.page_path}"

    class Meta:
        verbose_name = "User Interaction"
        verbose_name_plural = "User Interactions"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'type']),
        ]

    @property
    def offer_id(self):
        if self.type == 'offer_interest':
            return self.additional_data.get('offer_id', 'N/A')
        return 'N/A'


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('testimonials_cache')  # Optional future-proofing

    def delete(self, *args, **kwargs):
        cache.delete('testimonials_cache')
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Testimonial by {self.name}"


# models.py
# Add this new model for cookie consent tracking
class CookieConsent(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    analytics = models.BooleanField(default=False)
    preferences = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cookie Consent ({self.session_key})"


# models.py - Add this for analytics events
class AnalyticsEvent(models.Model):
    session_key = models.CharField(max_length=40)
    category = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    label = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255)
    value = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Add these new fields:
    event_value = models.IntegerField(default=0)
    is_conversion = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['category', 'action']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.category} - {self.action}"