from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('blocked/', views.blocked_view, name='blocked'),
    path('post/new/', views.AddPostView.as_view(), name='add_post'),
    path('post/<int:pk>/edit/', views.EditPostView.as_view(), name='edit_post'),
    path('post/<int:pk>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
