"""
URL configuration for casino project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for casino project.
"""
from django.contrib import admin
from django.urls import path, include
from app.admin import custom_admin_site
from app.views import (
    home,
    updates,
    subscribe,
    contact_submit,
    track_interaction,
    track_page_visit,
    cookie_consent,
    track_event, access_denied
)
urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('', home, name='home'),
    path('updates/', updates, name='updates'),
    path('subscribe/', subscribe, name='subscribe'),
    path('contact/', contact_submit, name='contact_submit'),
    path('track-interaction/', track_interaction, name='track_interaction'),
    path('track-visit/', track_page_visit, name='track_page_visit'),
    path('cookie-consent/', cookie_consent, name='cookie_consent'),
    path('track-event/', track_event, name='track_event'),
    path('access-denied/', access_denied, name='access_denied'),

]
handler403 = 'app.views.access_denied'
