# views.py
import json
import time
from django.db.models import F

from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.cache import cache
# views.py
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import json

from .models import LiveWin, Offer, PaymentMethod, SocialLink, UserInteraction, PageVisit, Testimonial
from django.contrib.admin.views.decorators import staff_member_required

# Cache keys
PAYMENT_METHODS_CACHE_KEY = 'payment_methods_cache'
SOCIAL_LINK_CACHE_KEY = 'social_link_cache'
OFFERS_CACHE_KEY = 'offers_cache'


def home(request):
    now = timezone.now()

    # Get offers with caching
    # Get offers with caching - clear cache after save in admin
    offers = cache.get(OFFERS_CACHE_KEY)  # Should be OFFERS_CACHE_KEY (plural)
    if not offers:
        offers = Offer.objects.filter(
            Q(countdown_end__gt=now) | Q(scheduled_start__gt=now),
            is_active=True  # Add this filter
        )
        cache.set(OFFERS_CACHE_KEY, offers, 300)

    # Find active and future offers
    active_offer = next((o for o in offers if o.scheduled_start <= now <= o.countdown_end), None)
    future_offer = next((o for o in offers if o.scheduled_start > now), None)

    # Get payment methods with caching
    payment_methods = cache.get(PAYMENT_METHODS_CACHE_KEY)
    if payment_methods is None:
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        cache.set(PAYMENT_METHODS_CACHE_KEY, payment_methods, 3600)  # Cache for 1 hour

    # Get social links with caching
    social = cache.get(SOCIAL_LINK_CACHE_KEY)
    if social is None:
        social = SocialLink.objects.first()
        cache.set(SOCIAL_LINK_CACHE_KEY, social, 3600)  # Cache for 1 hour

    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:5]


    context = {
        'live_wins': LiveWin.objects.filter(visible=True).order_by('-timestamp')[:10],
        'payment_methods': payment_methods,
        'social': social,
        'active_offer': active_offer,
        'future_offer': future_offer,
        'contact_form': ContactForm(),
        'tracking_enabled': True,  # Flag for frontend
        'testimonials': testimonials,

    }
    return render(request, 'casino/index.html', context)


def contact_submit(request):
    if request.method != 'POST':
        return redirect('home')

    form = ContactForm(request.POST)
    if not form.is_valid():
        for error in form.errors.values():
            messages.error(request, error[0])
        return redirect('home')

    form.save()
    messages.success(request, "Your message has been sent successfully!")
    return redirect('home')


# def updates(request):
#     def event_stream():
#         last_win_id = cache.get('last_win_id', 0)
#
#         while True:
#             # Get new wins using efficient filtering
#             new_wins = LiveWin.objects.filter(
#                 id__gt=last_win_id,
#                 visible=True
#             ).only('username', 'amount')
#
#             for win in new_wins:
#                 yield f"data: {json.dumps({'type': 'win', 'username': win.username, 'amount': str(win.amount)})}\n\n"
#                 last_win_id = win.id
#                 cache.set('last_win_id', last_win_id, 86400)  # Persist for 1 day
#
#             # Only process active offers
#             now = timezone.now()
#             active_offers = Offer.objects.filter(
#                 scheduled_start__lte=now,
#                 countdown_end__gt=now
#             ).only('id', 'countdown_end')
#
#             if active_offers:
#                 offers_data = [{
#                     'id': o.id,
#                     'countdown': int((o.countdown_end - now).total_seconds())
#                 } for o in active_offers]
#
#                 yield f"data: {json.dumps({'type': 'offers', 'offers': offers_data})}\n\n"
#
#             time.sleep(15)  # Update interval
#
#     return StreamingHttpResponse(
#         event_stream(),
#         content_type='text/event-stream',
#         headers={'Cache-Control': 'no-cache'}
#     )

@require_GET
@cache_page(15)  # Cache results for 15 seconds
def updates(request):
    now = timezone.now()

    # Get last_win_id from request parameter
    last_win_id = int(request.GET.get('last_win_id', 0))

    # Fetch new wins since last_win_id
    new_wins = LiveWin.objects.filter(
        id__gt=last_win_id,
        visible=True
    ).order_by('id').values('id', 'username', 'amount')[:100]  # Limit to 100 wins

    # Get active offers (countdown in progress)
    active_offers = Offer.objects.filter(
        scheduled_start__lte=now,
        countdown_end__gt=now,
        is_active=True
    ).values('id', 'countdown_end')

    # Calculate remaining seconds for each offer
    offers_data = []
    for offer in active_offers:
        time_remaining = (offer['countdown_end'] - now).total_seconds()
        offers_data.append({
            'id': offer['id'],
            'countdown': int(time_remaining)
        })

    # Get latest win ID for next request
    # latest_win_id = new_wins.last()['id'] if new_wins else last_win_id
    new_wins_list = list(new_wins)
    latest_win_id = new_wins_list[-1]['id'] if new_wins_list else last_win_id

    return JsonResponse({
        'wins': list(new_wins),
        'offers': offers_data,
        'last_win_id': latest_win_id
    })


# New view for recording interactions
@csrf_exempt
def track_interaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            interaction = UserInteraction(
                type=data.get('type'),
                element_id=data.get('element_id'),
                page_path=data.get('page_path', request.META.get('HTTP_REFERER', '/')),
                additional_data=data.get('data', {})
            )
            interaction.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)


# New view for analytics dashboard
@staff_member_required
def analytics_dashboard(request):
    # Today's stats
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    visits_today = PageVisit.objects.filter(timestamp__gte=today).count()

    # Popular content
    popular_pages = PageVisit.objects.values('path').annotate(
        visits=models.Count('id')
    ).order_by('-visits')[:10]

    # User interests
    offer_interest = UserInteraction.objects.filter(
        type='offer_interest'
    ).values('additional_data__offer_id').annotate(
        interactions=models.Count('id')
    ).order_by('-interactions')

    context = {
        'visits_today': visits_today,
        'popular_pages': popular_pages,
        'offer_interest': offer_interest,
    }
    return render(request, 'admin/analytics.html', context)


# tracks user page vists
# @csrf_exempt
# def track_page_visit(request):
#     if request.method != 'POST':
#         return JsonResponse({'status': 'invalid method'}, status=405)
#
#     try:
#         data = json.loads(request.body)
#         ip = request.META.get('REMOTE_ADDR')
#         country = data.get('country', 'Unknown')
#         session_key = request.session.session_key
#
#         # Check if we have an existing active session for this IP
#         existing_visit = None
#         try:
#             existing_visit = PageVisit.objects.get(
#                 ip_address=ip,
#                 is_active=True
#             )
#         except ObjectDoesNotExist:
#             pass
#         except PageVisit.MultipleObjectsReturned:
#             # Handle rare case of multiple active sessions
#             PageVisit.objects.filter(ip_address=ip, is_active=True).update(is_active=False)
#             existing_visit = None
#
#         if existing_visit:
#             # Update duration for existing session
#             duration = (timezone.now() - existing_visit.timestamp).total_seconds()
#             existing_visit.duration = int(duration)
#             existing_visit.save()
#         else:
#             # Create new session record
#             PageVisit.objects.create(
#                 ip_address=ip,
#                 country=country,
#                 session_key=session_key
#             )
#
#         return JsonResponse({'status': 'success'})
#
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# views.py



@csrf_exempt
def track_page_visit(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        ip = request.META.get('REMOTE_ADDR', 'Unknown')

        # Ensure country is never empty
        country = data.get('country', '').strip()
        if not country:
            country = 'Unknown'

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        now = timezone.now()

        with transaction.atomic():
            # Get or create session record
            visit, created = PageVisit.objects.select_for_update().get_or_create(
                session_key=session_key,
                defaults={
                    'ip_address': ip,
                    'country': country,
                    'timestamp': now,
                    'last_activity': now
                }
            )

            # Update existing record
            if not created:
                # Calculate time since last activity
                time_since_last = (now - visit.last_activity).total_seconds()

                # Only add to duration if user was active in last 5 minutes
                if time_since_last < 300:  # 5 minutes
                    visit.duration += int(time_since_last)

                # Update IP if changed
                if visit.ip_address != ip:
                    visit.ip_address = ip

                # Update country if previously unknown
                if visit.country == 'Unknown' and country != 'Unknown':
                    visit.country = country

                # Update last activity time
                visit.last_activity = now
                visit.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    # Simplified subscription logic
    return JsonResponse({'success': True})
