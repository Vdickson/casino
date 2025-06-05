# casino/urls.py
from django.urls import path
from . import views
from .views import contact_submit
from .views import track_interaction, analytics_dashboard


urlpatterns = [
    path('', views.home, name='home'),
    path('updates/', views.updates, name='updates'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('contact/', contact_submit, name='contact_submit'),

    # ... existing paths ...
    path('track-interaction/', track_interaction, name='track_interaction'),
    path('admin/analytics/', analytics_dashboard, name='analytics_dashboard'),


]