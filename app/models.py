# models.py
from django.db import models
from django.utils import timezone
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
        ]


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='payments/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class SocialLink(models.Model):
    facebook = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    telegram = models.URLField(blank=True)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)


# models.py - Add to existing models
class PageVisit(models.Model):
    path = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.path} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Page Visit"
        verbose_name_plural = "Page Visits"
        ordering = ['-timestamp']


class UserInteraction(models.Model):
    INTERACTION_TYPES = (
        ('button_click', 'Button Click'),
        ('form_submit', 'Form Submission'),
        ('link_click', 'Link Click'),
        ('offer_interest', 'Offer Interest'),
        ('payment_click', 'Payment Method Click'),
    )
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

    @property
    def offer_id(self):
        if self.type == 'offer_interest':
            return self.additional_data.get('offer_id', 'N/A')
        return 'N/A'