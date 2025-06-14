from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.home, name='home'),
    path('rechercher/', views.search_trips, name='search_trips'),
    path('reservation/<int:voyage_id>/', views.make_reservation, name='make_reservation'),
    path('connexion/', views.client_login, name='login'),
    path('inscription/', views.client_register, name='register'),
    path('deconnexion/', views.client_logout, name='logout'),
    path('ticket/<int:ticket_id>/receipt/', views.download_ticket_receipt, name='download_ticket_receipt'),
    path('ticket/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
    path('admin/reservations/day/', views.admin_reservations_by_day, name='admin_reservations_by_day'),
    path('admin/reservations/week/', views.admin_reservations_by_week, name='admin_reservations_by_week'),
   
]