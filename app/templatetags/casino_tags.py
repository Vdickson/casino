from django import template

register = template.Library()

@register.inclusion_tag('casino/offers.html')
def show_offers():
    return {'offers': ConstantOffer.objects.filter(is_active=True)}