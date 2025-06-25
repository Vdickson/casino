# views.py
import json
import time
from django.db.models import F
import logging
import requests
from django.views.decorators.http import require_GET
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
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Avg, Q, F
from datetime import timedelta
from django.utils import timezone
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import RechargeForm
from .models import LiveWin, Offer, PaymentMethod, SocialLink, UserInteraction, PageVisit, Testimonial, CookieConsent, \
    AnalyticsEvent
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)
# Cache keys
PAYMENT_METHODS_CACHE_KEY = 'payment_methods_cache'
SOCIAL_LINK_CACHE_KEY = 'social_link_cache'
OFFERS_CACHE_KEY = 'offers_cache'


def home(request):
    now = timezone.now()
    recommended_offers = []

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

    # Get user preferences from cookies
    user_preferences = {}
    if request.session.session_key:
        try:
            consent = CookieConsent.objects.get(session_key=request.session.session_key)
            user_preferences = {
                'analytics': consent.analytics,
                'marketing': consent.marketing
            }
        except CookieConsent.DoesNotExist:
            pass

    # Get recommended offers based on interactions
    show_personalization = False
    # Get user preferences from cookies
    user_preferences = {}
    show_personalization = False  # Initialize here

    if request.session.session_key:
        try:
            consent = CookieConsent.objects.get(session_key=request.session.session_key)
            if consent.marketing:
                # Get user's top 3 interested offers
                top_offer_ids = UserInteraction.objects.filter(
                    type='offer_interest',
                    page_visit__session_key=request.session.session_key  # Fix here
                ).values('additional_data__offer_id').annotate(
                    count=Count('id')
                ).order_by('-count')[:3]

                offer_ids = [item['additional_data__offer_id'] for item in top_offer_ids]
                recommended_offers = list(Offer.objects.filter(
                    id__in=offer_ids,
                    is_active=True
                ).values('id', 'title', 'description'))
        except CookieConsent.DoesNotExist:
            pass
        # Convert to JSON-safe format
    recommended_offers_json = json.dumps(recommended_offers)
    context = {
        'live_wins': LiveWin.objects.filter(visible=True).order_by('-timestamp')[:10],
        'payment_methods': payment_methods,
        'social': social,
        'active_offer': active_offer,
        'future_offer': future_offer,
        'contact_form': ContactForm(),
        'tracking_enabled': True,  # Flag for frontend
        'testimonials': testimonials,
        'user_preferences': user_preferences,
        'recommended_offers': recommended_offers,
        'show_personalization': user_preferences.get('marketing', False)

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
@cache_page(15)
def updates(request):
    now = timezone.now()
    last_win_id = int(request.GET.get('last_win_id', 0))

    try:
        new_wins = LiveWin.objects.filter(
            id__gt=last_win_id,
            visible=True
        ).order_by('id').values('id', 'username', 'amount')[:100]

        active_offers = Offer.objects.filter(
            scheduled_start__lte=now,
            countdown_end__gt=now,
            is_active=True
        ).values('id', 'countdown_end')

        offers_data = []
        for offer in active_offers:
            time_remaining = (offer['countdown_end'] - now).total_seconds()
            offers_data.append({
                'id': offer['id'],
                'countdown': int(time_remaining)
            })

        new_wins_list = list(new_wins)
        latest_win_id = new_wins_list[-1]['id'] if new_wins_list else last_win_id

        return JsonResponse({
            'wins': new_wins_list,
            'offers': offers_data,
            'last_win_id': latest_win_id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# New view for recording interactions
@csrf_exempt
def track_interaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            # Get or create the PageVisit record
            page_visit, created = PageVisit.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
                    'country': 'Unknown',  # Will be updated later
                    'path': data.get('page_path', '/')
                }
            )

            # Create the interaction
            interaction = UserInteraction(
                page_visit=page_visit,
                type=data.get('type'),
                element_id=data.get('element_id', ''),
                page_path=data.get('page_path', '/'),
                additional_data=data.get('additional_data', {})
            )
            interaction.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)


@csrf_exempt
def track_page_visit(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
        path = data.get('path', '/')  # Get path from request

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
                    'path': path,
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

                if 'path' in data:  # Update path if provided
                    visit.path = data['path']

                # Update last activity time
                visit.last_activity = now
                visit.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# views.py
@csrf_exempt
def cookie_consent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            # Create or update consent record
            consent, created = CookieConsent.objects.update_or_create(
                session_key=session_key,
                defaults={
                    'analytics': data.get('analytics', False),
                    'preferences': data.get('preferences', False),
                    'marketing': data.get('marketing', False),
                    'timestamp': timezone.now()
                }
            )

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error saving cookie consent: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid method'}, status=405)

@csrf_exempt
def track_event(request):
    if request.method == 'POST':
        try:
            # Get session key
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            # Parse JSON data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'invalid_json'}, status=400)

            # Check consent - first try database, then fallback to localStorage
            try:
                consent = CookieConsent.objects.get(session_key=session_key)
                if not consent.analytics:
                    return JsonResponse({'status': 'no_analytics_consent'}, status=403)
            except CookieConsent.DoesNotExist:
                # If no record exists, check request headers for localStorage fallback
                localStorageConsent = request.headers.get('X-Consent-Analytics', 'false') == 'true'
                if not localStorageConsent:
                    return JsonResponse({'status': 'no_consent'}, status=403)

            # Save event
            event = AnalyticsEvent(
                session_key=session_key,
                category=data.get('category', ''),
                action=data.get('action', ''),
                label=data.get('label', ''),
                value=data.get('value', 0),
                path=data.get('path', request.path),
                timestamp=timezone.now()
            )
            event.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid_method'}, status=405)
# views.py
# Update the analytics_dashboard view
@staff_member_required
def analytics_dashboard(request):
    # Time ranges
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    now = timezone.now()

    # Basic metrics
    visits_today = PageVisit.objects.filter(timestamp__date=today.date()).count()
    visits_yesterday = PageVisit.objects.filter(timestamp__date=yesterday.date()).count()
    total_visits = PageVisit.objects.count()
    visit_change = ((visits_today - visits_yesterday) / visits_yesterday * 100) if visits_yesterday else 0

    # Consent metrics
    # total_consent = CookieConsent.objects.count()
    # analytics_consent = CookieConsent.objects.filter(analytics=True).count()
    # consent_rate = (analytics_consent / total_consent * 100) if total_consent else 0

    total_visitors = PageVisit.objects.count()
    analytics_consent = CookieConsent.objects.filter(analytics=True).count()
    consent_rate = (analytics_consent / total_visitors * 100) if total_visitors else 0

    # Engagement metrics
    avg_duration = PageVisit.objects.aggregate(avg=Avg('duration'))['avg'] or 0
    bounce_count = PageVisit.objects.filter(duration__lt=5).count()
    bounce_rate = (bounce_count / total_visits * 100) if total_visits else 0

    # Conversion metrics
    conversions = UserInteraction.objects.filter(type='form_submit').count()
    conversion_rate = (conversions / visits_today * 100) if visits_today else 0

    # Popular pages
    popular_pages = PageVisit.objects.values('path').annotate(
        visits=Count('id'),
        avg_duration=Avg('duration'),
    ).annotate(
        bounce_count=Count('id', filter=Q(duration__lt=5))
    ).order_by('-visits')[:10]

    for page in popular_pages:
        page['bounce_rate'] = (page['bounce_count'] / page['visits'] * 100) if page['visits'] else 0

    # Top events
    top_events = AnalyticsEvent.objects.values('category', 'action').annotate(
        count=Count('id'),
        avg_value=Avg('value')
    ).order_by('-count')[:10]

    # Offer performance
    offer_performance = []
    for offer in Offer.objects.all():
        views = UserInteraction.objects.filter(
            type='offer_interest',
            additional_data__offer_id=offer.id
        ).count()

        conversions = UserInteraction.objects.filter(
            type='form_submit',
            additional_data__offer_title=offer.title
        ).count()

        conversion_rate_val = (conversions / views * 100) if views else 0

        offer_performance.append({
            'title': offer.title,
            'views': views,
            'conversions': conversions,
            'conversion_rate': conversion_rate_val
        })

    # User interests
    user_interests = AnalyticsEvent.objects.values('category').annotate(
        count=Count('id'),
        unique_users=Count('session_key', distinct=True)
    ).order_by('-count')[:10]

    # Conversion funnel
    funnel_steps = [
        {'name': 'Visitors', 'count': total_visits},
        {'name': 'Engaged Visitors', 'count': PageVisit.objects.filter(duration__gte=10).count()},
        {'name': 'Offer Views', 'count': UserInteraction.objects.filter(type='offer_interest').count()},
        {'name': 'Contact Initiated', 'count': UserInteraction.objects.filter(
            type='button_click', element_id__contains='contact').count()},
        {'name': 'Form Submissions', 'count': conversions}
    ]

    # Calculate percentages for funnel
    for i, step in enumerate(funnel_steps):
        if i == 0:
            step['percent'] = 100
        else:
            step['percent'] = (step['count'] / funnel_steps[0]['count'] * 100) if funnel_steps[0]['count'] else 0

    # Time-based metrics
    daily_visits = []
    for i in range(7, -1, -1):
        date = today - timedelta(days=i)
        count = PageVisit.objects.filter(timestamp__date=date).count()
        daily_visits.append({'date': date.strftime('%a'), 'count': count})

    # Last 30 minutes activity
    # Update the recent_activity query to:
    recent_activity = AnalyticsEvent.objects.filter(
        timestamp__gte=now - timedelta(minutes=30)
    ).select_related('page_visit').order_by('-timestamp')[:20]

    context = {
        'visits_today': visits_today,
        'visit_change': visit_change,
        'total_visits': total_visits,
        'consent_rate': consent_rate,
        'avg_duration': avg_duration,
        'bounce_rate': bounce_rate,
        'conversion_rate': conversion_rate,
        'popular_pages': popular_pages,
        'top_events': top_events,
        'offer_performance': offer_performance,
        'user_interests': user_interests,
        'conversion_funnel': funnel_steps,
        'daily_visits': daily_visits,
        'recent_activity': recent_activity,
    }
    return render(request, 'admin/analytics_dashboard.html', context)


@login_required
def recharge(request):
    payment_methods = PaymentMethod.objects.filter(is_active=True)

    if request.method == 'POST':
        form = RechargeForm(request.POST, request.FILES)
        if form.is_valid():
            recharge = form.save(commit=False)
            recharge.player = request.user
            recharge.save()

            track_interaction({
                'type': 'recharge_request',
                'page_path': request.path,
                'data': {
                    'amount': str(recharge.amount),
                    'method': recharge.payment_method.name
                }
            })

            messages.success(request, "Recharge request submitted! We'll process it shortly.")
            return redirect('home')
    else:
        form = RechargeForm()

    context = {
        'payment_methods': payment_methods,
        'form': form
    }
    return render(request, 'casino/recharge.html', context)


def subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    # Simplified subscription logic
    return JsonResponse({'success': True})


# views.py
def get_personalized_ads(request):
    if not request.session.session_key:
        return []

    try:
        # Get user's interaction history
        interactions = UserInteraction.objects.filter(
            session_key=request.session.session_key
        ).order_by('-timestamp')[:100]

        # Simple scoring algorithm
        offer_scores = {}
        for interaction in interactions:
            if interaction.type == 'offer_click':
                offer_id = interaction.data.get('offer_id')
                if offer_id:
                    offer_scores[offer_id] = offer_scores.get(offer_id, 0) + 3
            elif interaction.type == 'game_play':
                game = interaction.data.get('game')
                if game:
                    # Add score to related offers
                    related_offers = Offer.objects.filter(
                        Q(title__icontains=game) |
                        Q(description__icontains=game)
                    )
                    for offer in related_offers:
                        offer_scores[offer.id] = offer_scores.get(offer.id, 0) + 1

        # Get top 3 offers
        sorted_offers = sorted(offer_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        offer_ids = [offer[0] for offer in sorted_offers]

        return Offer.objects.filter(id__in=offer_ids)
    except Exception:
        return []


# views.py

def access_denied(request, exception=None):
    return render(request, 'casino/403.html', status=403)

