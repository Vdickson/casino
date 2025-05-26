from django.db import models
from django.utils import timezone
from django.db.models import Q


class LiveWin(models.Model):
    username = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    visible = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_start = models.DateTimeField()
    duration_hours = models.PositiveIntegerField(default=24)
    countdown_end = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Calculate countdown_end based on duration
        if self.scheduled_start and self.duration_hours:
            self.countdown_end = self.scheduled_start + timezone.timedelta(hours=self.duration_hours)
            # Automatically activate if within scheduled time
            now = timezone.now()
            self.is_active = self.scheduled_start <= now <= self.countdown_end
        super().save(*args, **kwargs)

    @property
    def time_until_start(self):
        if timezone.now() < self.scheduled_start:
            return self.scheduled_start - timezone.now()
        return None

    @property
    def time_remaining(self):
        if self.is_active:
            return self.countdown_end - timezone.now()
        return None

    @classmethod
    def get_upcoming_offer(cls):
        now = timezone.now()
        return cls.objects.filter(
            Q(countdown_end__gt=now) |
            Q(scheduled_start__gt=now)
        ).order_by('scheduled_start').first()


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='payments/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)


class SocialLink(models.Model):
    facebook = models.URLField()
    whatsapp = models.URLField()
    telegram = models.URLField()


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
