from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'registration'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    path('set-language/', views.set_language, name='set_language'),
    path('register/', views.registration_selection, name='registration_selection'),
    path('contact/', views.contact_form_submit, name='contact_form'),
    
    # Household URLs
    path('household/signup/', views.household_signup, name='household_signup'),
    path('household/login/', views.household_login, name='household_login'),
    path('household/dashboard/', views.household_dashboard, name='household_dashboard'),
    path('household/requests/', views.household_requests, name='household_requests'),
    path('household/notifications/', views.household_notifications, name='household_notifications'),
    path('household/profile/', views.household_profile, name='household_profile'),
    path('household/history/', views.household_history, name='household_history'),
    path('household/settings/', views.household_settings, name='household_settings'),
    path('household/help/', views.household_help, name='household_help'),
    
    # Collector URLs
    path('collector/signup/', views.collector_signup, name='collector_signup'),
    path('collector/login/', views.collector_login, name='collector_login'),
    path('collector/dashboard/', views.collector_dashboard, name='collector_dashboard'),
    path('collector/available/', views.collector_available, name='collector_available'),
    path('collector/assigned/', views.collector_assigned, name='collector_assigned'),
    path('collector/profile/', views.collector_profile_view, name='collector_profile'),
    
    # Admin URLs (renamed prefix to avoid conflict with Django admin.site)
    path('portal-admin/login/', views.admin_login, name='admin_login'),
    path('portal-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('portal-admin/pickups/', views.admin_pickups, name='admin_pickups'),
    path('portal-admin/households/', views.admin_households, name='admin_households'),
    path('portal-admin/collectors/', views.admin_collectors, name='admin_collectors'),
    path('portal-admin/quick-actions/', views.admin_quick_actions, name='admin_quick_actions'),
    
    # Password reset (shared by all user types)
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
    
    # Utility URLs
    path('logout/', views.logout_view, name='logout'),
    path('pickup/create/', views.create_pickup_request, name='create_pickup_request'),
    path('pickup/<int:pickup_id>/assign/', views.assign_pickup, name='assign_pickup'),
    
    # AJAX endpoints for cascading dropdowns
    path('api/districts/', views.get_districts, name='get_districts'),
    path('api/sectors/', views.get_sectors, name='get_sectors'),
    path('api/cells/', views.get_cells, name='get_cells'),
    path('api/villages/', views.get_villages, name='get_villages'),
    
    # OTP endpoints
    path('api/send-otp/', views.request_otp, name='send_otp'),
    path('api/request-otp/', views.request_otp, name='request_otp'),
    path('api/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/resend-otp/', views.resend_otp, name='resend_otp'),
    
    # Chatbot endpoint
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    
    # Geolocation and map endpoints
    path('api/nearby-collectors/', views.get_nearby_collectors, name='nearby_collectors'),
    path('api/nearby-pickups/', views.get_nearby_pickups, name='nearby_pickups'),
    path('api/update-location/', views.update_location, name='update_location'),
]
