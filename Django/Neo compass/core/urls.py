from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    # Student
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile_edit, name='student_profile'),
    path('student/domain/leave/', views.leave_domain, name='leave_domain'),
    path('student/domains/', views.student_domains, name='student_domains'),
    path('student/domain/<int:domain_id>/', views.domain_detail, name='domain_detail'),
    path('student/assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/quizzes/', views.student_quizzes, name='student_quizzes'),
    path('student/quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('student/achievements/', views.achievements_feed, name='achievements_feed'),
    path('student/achievement/post/', views.post_achievement, name='post_achievement'),
    path('student/achievement/<int:achievement_id>/edit/', views.edit_achievement, name='edit_achievement'),
    path('student/achievement/<int:achievement_id>/delete/', views.delete_achievement, name='delete_achievement'),
    path('student/leaderboard/', views.leaderboard, name='leaderboard'),
    path('student/placement/', views.placement_guide, name='placement_guide'),
    path('student/feedback/', views.submit_feedback, name='submit_feedback'),
    path('student/request-topic/', views.request_topic, name='request_topic'),
    
    # Mentor
    path('mentor/dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('mentor/handle-topic-request/<int:request_id>/', views.handle_topic_request, name='handle_topic_request'),
    path('mentor/reset-domain-topics/<int:domain_id>/', views.reset_domain_topics, name='reset_domain_topics'),

    path('mentor/students/', views.mentor_students, name='mentor_students'),

    path('mentor/quick-approve/<int:profile_id>/', views.mentor_quick_approve, name='mentor_quick_approve'),
    path('mentor/domains/', views.mentor_domains, name='mentor_domains'),
    path('mentor/domain/<int:domain_id>/edit/', views.mentor_edit_domain, name='mentor_edit_domain'),
    path('mentor/domain/<int:domain_id>/delete/', views.mentor_delete_domain, name='mentor_delete_domain'),
    path('hod/add-domain/', views.hod_add_domain, name='hod_add_domain'),

    path('mentor/domain/<int:domain_id>/add-resource/', views.add_resource, name='mentor_add_resource'),
    path('mentor/domain/<int:domain_id>/add-assignment/', views.add_assignment, name='mentor_add_assignment'),
    path('mentor/domain/<int:domain_id>/curriculum/', views.mentor_domain_curriculum, name='mentor_domain_curriculum'),
    path('mentor/resource/<int:resource_id>/edit/', views.mentor_edit_resource, name='mentor_edit_resource'),
    path('mentor/resource/<int:resource_id>/delete/', views.mentor_delete_resource, name='mentor_delete_resource'),
    path('mentor/assignment/<int:assignment_id>/edit/', views.mentor_edit_assignment, name='mentor_edit_assignment'),
    path('mentor/assignment/<int:assignment_id>/delete/', views.mentor_delete_assignment, name='mentor_delete_assignment'),
    
    path('mentor/grade-submissions/', views.grade_submissions, name='grade_submissions'),

    path('mentor/grade-submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    
    # HOD
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('hod/users/', views.hod_users, name='hod_users'),
    path('hod/approve-student/<int:profile_id>/', views.hod_approve_student, name='hod_approve_student'),
    path('hod/toggle-user/<int:user_id>/', views.hod_toggle_user, name='hod_toggle_user'),
    path('hod/change-role/<int:user_id>/', views.hod_change_role, name='hod_change_role'),
    path('hod/graduate-student/<int:user_id>/', views.hod_graduate_student, name='hod_graduate_student'),
    path('alumni/update-profile/<int:user_id>/', views.update_alumni_profile, name='update_alumni_profile'),
    path('hod/feedback/', views.hod_feedback, name='hod_feedback'),
    path('hod/domains/', views.hod_domains, name='hod_domains'),
    path('hod/domain/<int:domain_id>/allocate/', views.hod_allocate_mentors, name='hod_allocate_mentors'),
    
    # Alumni
    path('alumni/posts/', views.alumni_posts, name='alumni_posts'),
    path('alumni/posts/add/', views.add_alumni_post, name='add_alumni_post'),
    path('alumni/profile/<int:user_id>/', views.alumni_profile, name='alumni_profile'),
    path('alumni/add/', views.add_alumni, name='add_alumni'),

    
    # Social
    path('achievement/<int:achievement_id>/like/', views.like_achievement, name='like_achievement'),
    path('achievement/<int:achievement_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('hod/add-placement/', views.add_placement_resource, name='add_placement_resource'),
]
