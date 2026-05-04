from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Patient
    path('', views.home, name='home'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('slots/<int:doctor_id>/', views.available_slots, name='available_slots'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),

    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/doctors/', views.manage_doctors, name='manage_doctors'),
    path('admin-dashboard/doctors/add/', views.add_doctor, name='add_doctor'),
    path('admin-dashboard/doctors/edit/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('admin-dashboard/doctors/delete/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('admin-dashboard/slots/', views.manage_slots, name='manage_slots'),
    path('admin-dashboard/slots/add/', views.add_slot, name='add_slot'),
    path('admin-dashboard/slots/delete/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    path('admin-dashboard/appointments/', views.all_appointments, name='all_appointments'),
    path('admin-dashboard/appointments/cancel/<int:appointment_id>/', views.admin_cancel_appointment, name='admin_cancel_appointment'),
    path('admin-dashboard/patients/', views.manage_patients, name='manage_patients'),
    path('admin-dashboard/patients/delete/<int:user_id>/', views.delete_patient, name='delete_patient'),
]