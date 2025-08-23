from django.urls import path
from . import views
app_name = "coordinator"
urlpatterns = [
    path('',views.index,name="index"),
    path("login/",views.userlogin,name="userlogin"),
    path("register/",views.userregister,name="userregister"),
    path("logout/",views.userlogout,name="logout"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("delete_event/",views.delete_event,name="delete_event"),
    path("add_gallery/",views.add_gallery,name="add_gallery"),
    path("delete_gallery/",views.delete_gallery,name="delete_gallery"),
    path("gallery/",views.gallery,name="gallery"),
    path("event/",views.event,name="event"),
    path("add_form/",views.add_form,name="add_form"),
    path("edit_form/",views.edit_form,name="edit_form"),
]
