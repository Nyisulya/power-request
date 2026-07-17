from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('submit-testimony/', views.submit_testimony, name='submit_testimony'),
    path('leader/', views.leader_panel, name='leader_panel'),
    path('about/', views.about, name='about'),
    path('requests/', views.requests_room, name='requests_room'),
    path('testimonies/', views.testimonies_room, name='testimonies_room'),
    path('giving/', views.giving, name='giving'),
]
