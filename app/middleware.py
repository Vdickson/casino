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
