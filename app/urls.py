# casino/urls.py
from django.urls import path
from . import views
from .views import contact_submit

urlpatterns = [
    path('', views.home, name='home'),
    path('updates/', views.updates, name='updates'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('contact/', contact_submit, name='contact_submit'),

]