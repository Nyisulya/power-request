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
    path('register/', views.submit_registration, name='submit_registration'),
    path('quiz/get/', views.get_daily_question, name='get_daily_question'),
    path('quiz/start/', views.start_quiz_session, name='start_quiz_session'),
    path('quiz/submit/', views.submit_quiz_answer, name='submit_quiz_answer'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/members/', views.dashboard_members_view, name='dashboard_members'),
    path('dashboard/offerings/', views.dashboard_offerings_view, name='dashboard_offerings'),
    path('dashboard/leaders/', views.dashboard_leaders_view, name='dashboard_leaders'),
    path('dashboard/settings/', views.dashboard_settings_view, name='dashboard_settings'),
    path('dashboard/content/', views.dashboard_content_view, name='dashboard_content'),
    path('dashboard/submissions/', views.dashboard_submissions_view, name='dashboard_submissions'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('giving/checkout/', views.giving_checkout, name='giving_checkout'),
    path('pesapal/ipn/', views.pesapal_ipn, name='pesapal_ipn'),
    path('pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
    
    # Sermons (Mafundisho)
    path('sermons/', views.sermons_list_view, name='sermons_list'),
    path('sermons/series/<int:series_id>/', views.sermon_series_detail_view, name='sermon_series_detail'),
    path('dashboard/sermons/', views.dashboard_sermons_view, name='dashboard_sermons'),
    # SEO & Search Console
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('sw.js', views.sw_js, name='sw_js'),
]
