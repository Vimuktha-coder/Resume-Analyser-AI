# analyzerapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pricing/', views.pricing, name='pricing'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),
    
    # User auth
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('analytics/', views.user_analytics, name='user_analytics'),
    
    # Social login direct (bypass confirmation page)
    path('auth/google/', views.google_login_direct, name='google_login_direct'),
    path('auth/facebook/', views.facebook_login_direct, name='facebook_login_direct'),
    
    # Resume & Interview
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('update_user_role/', views.update_user_role, name='update_user_role'),
    path('interview/', views.start_interview, name='start_interview'),
    path('upload_interview_video/', views.upload_interview_video, name='upload_interview_video'),
    path('feedback/', views.interview_feedback, name='interview_feedback'),
    
    # Admin
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_candidates/', views.admin_candidates, name='admin_candidates'),
    path('admin_interviews/', views.admin_interviews, name='admin_interviews'),
    path('admin_feedback/', views.admin_feedback, name='admin_feedback'),
    path('admin_analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin_settings/', views.admin_settings, name='admin_settings'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('score/<int:id>/', views.score_interview, name='score_interview'),
    path('accept/<int:id>/', views.accept_interview, name='accept_interview'),
    path('reject/<int:id>/', views.reject_interview, name='reject_interview'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('resume_upload/', views.resume_upload, name='resume_upload'),
    path('start_interview/', views.start_interview, name='start_interview'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('transcript_doc/<int:candidate_id>/', views.download_transcript_doc, name='download_transcript_doc'),
    path('update_status/<int:candidate_id>/', views.update_status, name='update_status'),
    path('delete_candidate/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('logout/', views.user_logout, name='user_logout'),

]

