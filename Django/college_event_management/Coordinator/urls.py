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
    path("profile/",views.profile,name="profile"),
    path("approve_students/",views.approve_students,name="approve_students"),
    path("mcq/",views.mcq,name="mcq"),
    path("create_mcq/",views.create_mcq,name="create_mcq"),
    path("edit_mcq/<int:mcq_id>/",views.edit_mcq,name="edit_mcq"),
    path("delete_mcq/<int:mcq_id>/",views.delete_mcq,name="delete_mcq"),
    path("toggle_mcq_status/<int:mcq_id>/",views.toggle_mcq_status,name="toggle_mcq_status"),

]
