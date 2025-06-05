from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Offer, PaymentMethod, SocialLink

@receiver([post_save, post_delete], sender=Offer)
def clear_offer_cache(sender, **kwargs):
    cache.delete('offers_cache')

@receiver([post_save, post_delete], sender=PaymentMethod)
def clear_payment_cache(sender, **kwargs):
    cache.delete('payment_methods_cache')

@receiver([post_save, post_delete], sender=SocialLink)
def clear_social_cache(sender, **kwargs):
    cache.delete('social_link_cache')