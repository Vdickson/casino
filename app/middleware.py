# middleware.py
import geoip2.database
from django.conf import settings
from django.utils import timezone


class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip_reader = None
        if hasattr(settings, 'GEOIP_PATH'):
            try:
                self.geoip_reader = geoip2.database.Reader(settings.GEOIP_PATH)
            except:
                pass

    def __call__(self, request):
        # Defer model import to avoid circular dependencies
        from .models import PageVisit

        if not request.path.startswith('/admin') and not request.path.startswith('/static'):
            ip = self.get_client_ip(request)
            country = None

            if self.geoip_reader and ip:
                try:
                    response = self.geoip_reader.country(ip)
                    country = response.country.iso_code
                except:
                    pass

            PageVisit.objects.create(
                path=request.path,
                ip_address=ip,
                country=country
            )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')