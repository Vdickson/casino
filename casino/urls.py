from django.contrib import admin
from django.urls import path, include
from app.admin import custom_admin_site
from app import views  # Import all views from one place

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.home, name='home'),
    path('updates/', views.updates, name='updates'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('contact/', views.contact_submit, name='contact_submit'),
    path('track-interaction/', views.track_interaction, name='track_interaction'),
    path('track-visit/', views.track_page_visit, name='track_page_visit'),
    path('cookie-consent/', views.cookie_consent, name='cookie_consent'),
    path('track-event/', views.track_event, name='track_event'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('recharge/', views.recharge, name='recharge'),



]

handler403 = 'app.views.access_denied'
