# app/middleware.py
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
    # Add this at the top of the class
    TEST_WHITELIST_IPS = {
        "127.0.0.1",  # Replace with your Kenyan test IP
    }
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
        except:
            logger.warning("GeoIP2 database not available")

    def __call__(self, request):
        # # Allow bypass for testing (e.g., ?force_country=US)
        # if request.GET.get('force_country'):
        #     return self.get_response(request)
        # Skip admin/static files
        if request.path.startswith(('/admin/', '/static/', '/media/')) or request.path == reverse('access_denied'):
            return self.get_response(request)

        # Get client IP
        client_ip, _ = get_client_ip(request)
        print(f"🌐 Detected IP: {client_ip}")  # Debug log

        # Allow whitelisted IPs (even if from Africa)
        if client_ip in self.TEST_WHITELIST_IPS:
            print("✅ Whitelisted IP allowed (testing mode)")
            return self.get_response(request)

        # Block African countries
        country = self.get_country_from_ip(client_ip)
        if country in self.AFRICAN_COUNTRIES:
            return redirect('access_denied')

        return self.get_response(request)
    def get_country_from_ip(self, ip):
        cache_key = f'ip_country_{ip}'
        country = cache.get(cache_key)
        if country:
            return country

        # 1. Try local GeoIP database first
        if self.geoip_reader:
            try:
                response = self.geoip_reader.country(ip)
                country = response.country.iso_code
                cache.set(cache_key, country, 86400)
                return country
            except:
                pass

        try:
            # Try primary service
            response = requests.get(f"https://ipapi.co/{ip}/country/", timeout=2)
            if response.status_code == 200:
                country = response.text.strip()
                if country:  # Cache only valid responses
                    cache.set(cache_key, country, 86400)  # 24 hours
                return country
        except Exception as e:
            logger.warning(f"ipapi.co failed for {ip}: {str(e)}")

        try:
            # Fallback service
            response = requests.get(f"https://ipinfo.io/{ip}/country", timeout=2)
            if response.status_code == 200:
                country = response.text.strip()
                if country:
                    cache.set(cache_key, country, 86400)
                return country
        except Exception as e:
            logger.error(f"Country detection failed for {ip}: {str(e)}")

        return None  # Detection failed
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
