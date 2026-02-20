from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('chat/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('send_message/', views.send_message, name='send_message'),
    path('send_message/<int:conversation_id>/', views.send_message, name='send_message_to_conversation'),
    path('new_conversation/', views.new_conversation, name='new_conversation'),
    path('delete_conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('rename_conversation/<int:conversation_id>/', views.rename_conversation, name='rename_conversation'),
    path('clear_conversation/<int:conversation_id>/', views.clear_conversation, name='clear_conversation'),
    path('settings/', views.settings_view, name='settings'),
    path('upload_documents/', views.upload_documents, name='upload_documents'),
    path('clear_library/', views.clear_library, name='clear_library'),
    path('delete_document/<int:document_id>/', views.delete_document, name='delete_document'),
    path('upload_progress/', views.upload_progress, name='upload_progress'),
]
