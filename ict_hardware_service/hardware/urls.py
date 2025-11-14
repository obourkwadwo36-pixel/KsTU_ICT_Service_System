from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # existing ones
    path('create/', views.create_request, name='create_request'),
    path('request/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('request/<int:pk>/delete_staff/', views.delete_staff_request, name='delete_staff_request'),
    path('update/<int:request_id>/', views.add_job_update, name='add_job_update'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('ict_officer_dashboard/', views.ict_officer_dashboard, name='ict_officer_dashboard'),
    path('assign_technician/<int:pk>/', views.assign_technician, name='assign_technician'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('technician_job_history/', views.technician_job_history, name='technician_job_history'),
    path('ict_officer_job_history/', views.ict_officer_job_history, name='ict_officer_job_history'),

]
