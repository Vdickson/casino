# middleware.py
import requests
from django.http import HttpResponseForbidden
from ipware import get_client_ip
from django.urls import reverse
from django.shortcuts import redirect
import logging
from django.core.cache import cache
import geoip2.database

from casino import settings

logger = logging.getLogger(__name__)


class CountryRestrictionMiddleware:
    # List of African country codes to block
    AFRICAN_COUNTRIES = {
        'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CV', 'CM', 'CF', 'TD', 'KM', 'CG',
        'CD', 'DJ', 'EG', 'GQ', 'ER', 'SZ', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW',
        'CI', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'YT', 'MA',
        'MZ', 'NA', 'NE', 'NG', 'RE', 'RW', 'SH', 'ST', 'SN', 'SC', 'SL', 'SO',
        'ZA', 'SS', 'SD', 'TZ', 'TG', 'TN', 'UG', 'EH', 'ZM', 'ZW'
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip_reader = None
        try:
            self.geoip_reader = geoip2.database.Reader(settings.GEOIP_PATH)
        except Exception as e:
            logger.error(f"Failed to load GeoIP database: {str(e)}")

    def __call__(self, request):
        # Skip admin/static/media files and access denied page
        if request.path.startswith(('/admin/', '/static/', '/media/')) or request.path == reverse('access_denied'):
            return self.get_response(request)

        # Get client IP
        client_ip, is_routable = get_client_ip(request)

        # If no IP could be determined, block access to be safe
        if client_ip is None:
            logger.warning("Could not determine client IP - blocking access")
            return redirect('access_denied')

        # Check if IP is from an African country
        country = self.get_country_from_ip(client_ip)
        if country in self.AFRICAN_COUNTRIES:
            logger.info(f"Blocking access from African country: {country} (IP: {client_ip})")
            return redirect('access_denied')

        return self.get_response(request)

    def get_country_from_ip(self, ip):
        cache_key = f'ip_country_{ip}'
        country = cache.get(cache_key)
        if country:
            return country

        # Try local GeoIP database first (most reliable)
        if self.geoip_reader:
            try:
                response = self.geoip_reader.country(ip)
                country = response.country.iso_code
                if country:
                    cache.set(cache_key, country, 86400)  # Cache for 24 hours
                    return country
            except Exception as e:
                logger.warning(f"GeoIP lookup failed for {ip}: {str(e)}")

        # Fallback to ipapi.co
        try:
            response = requests.get(
                f"https://ipapi.co/{ip}/country/",
                headers={'User-Agent': 'django-country-restriction'},
                timeout=2
            )
            if response.status_code == 200:
                country = response.text.strip()
                if country:
                    cache.set(cache_key, country, 86400)
                    return country
        except Exception as e:
            logger.warning(f"ipapi.co lookup failed for {ip}: {str(e)}")

        # Final fallback to ipinfo.io
        try:
            response = requests.get(
                f"https://ipinfo.io/{ip}/country",
                headers={'User-Agent': 'django-country-restriction'},
                timeout=2
            )
            if response.status_code == 200:
                country = response.text.strip()
                if country:
                    cache.set(cache_key, country, 86400)
                    return country
        except Exception as e:
            logger.warning(f"ipinfo.io lookup failed for {ip}: {str(e)}")

        logger.error(f"All country detection methods failed for IP: {ip}")
        return None  # Could not determine country
# # # middleware.py
# # import geoip2.database
# # from django.conf import settings
# # from django.utils import timezone
# # from .models import PageVisit
# #
# # # middleware.py (ONLY USE IF YOU MUST KEEP MIDDLEWARE)
# # from django.utils import timezone
# # from .models import PageVisit
# #
# #
# # class PageVisitMiddleware:
# #     def __init__(self, get_response):
# #         self.get_response = get_response
# #
# #     def __call__(self, request):
# #         response = self.get_response(request)
# #
# #         # Skip admin/static requests
# #         if request.path.startswith('/admin') or request.path.startswith('/static'):
# #             return response
# #
# #         # Create session if needed
# #         if not request.session.session_key:
# #             request.session.create()
# #
# #         # Get or create PageVisit
# #         ip = request.META.get('REMOTE_ADDR', 'Unknown')
# #         PageVisit.objects.update_or_create(
# #             session_key=request.session.session_key,
# #             defaults={
# #                 'ip_address': ip,
# #                 'country': 'Unknown',  # Will be updated by JavaScript
# #                 'timestamp': timezone.now()
# #             }
# #         )
# #
# #         return response
# #
# # # class SessionDurationMiddleware:
# # #     def __init__(self, get_response):
# # #         self.get_response = get_response
# # #
# # #     def __call__(self, request):
# # #         response = self.get_response(request)
# # #         return response
# # #
# # #     def process_response(self, request, response):
# # #         # Only process if we have a session
# # #         if hasattr(request, 'session') and request.session.session_key:
# # #             session_key = request.session.session_key
# # #             ip = request.META.get('REMOTE_ADDR')
# # #
# # #             try:
# # #                 # Find active visit for this session
# # #                 visit = PageVisit.objects.get(
# # #                     session_key=session_key,
# # #                     ip_address=ip,
# # #                     is_active=True
# # #                 )
# # #
# # #                 # Calculate duration and close session
# # #                 duration = (timezone.now() - visit.timestamp).total_seconds()
# # #                 visit.duration = int(duration)
# # #                 visit.is_active = False
# # #                 visit.save()
# # #             except PageVisit.DoesNotExist:
# # #                 pass
# # #
# # #         return response
#
# from django.utils import timezone
#
#
# class UserTimezoneMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         if request.user.is_authenticated:
#             timezone.activate(request.user.timezone)  # User profile field
#         return self.get_response(request)
