from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('send/', views.send_message, name='send_message'),
    path('new/', views.new_session, name='new_chat_session'),
]
