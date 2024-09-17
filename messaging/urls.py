from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<int:pk>/', views.view_message, name='view_message'),

    path('sent/', views.sent_messages, name='sent_messages'),
]
