from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, StudentProfileForm, DomainForm, ResourceForm, AssignmentForm, AssignmentSubmissionForm, GradeSubmissionForm, QuizForm, AchievementForm, FeedbackForm, PostForm, AlumniForm, TopicRequestForm
from .models import User, StudentProfile, Domain, Resource, Assignment, AssignmentStatus, Quiz, QuizResult, PlacementResource, Alumni, Post, Achievement, Like, Comment, Feedback, TopicRequest
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

# --- AUTH ---
def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'student':
                StudentProfile.objects.create(user=user)
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard_redirect(request):
    if request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role in ['mentor', 'rep']:
        return redirect('mentor_dashboard')
    elif request.user.role == 'hod':
        return redirect('hod_dashboard')
    elif request.user.role == 'alumni':
        return redirect('alumni_posts')
    return redirect('home')


# --- STUDENT ---
@login_required
def student_dashboard(request):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    if profile.approval_status != 'APPROVED':
        available_domains = Domain.objects.all()
        return render(request, 'student/pending.html', {
            'profile': profile,
            'available_domains': available_domains
        })
    
    must_select_domain = profile.preferred_domain is None
    
    domain_progress = 0
    completed_assignments = 0
    total_assignments = 0
    pending_quizzes = 0
    
    if profile.preferred_domain:
        # Calculate Assignment Progress
        total_assignments = Assignment.objects.filter(domain=profile.preferred_domain).count()
        completed_assignments = AssignmentStatus.objects.filter(
            student=request.user, 
            assignment__domain=profile.preferred_domain, 
            completed=True
        ).count()
        if total_assignments > 0:
            domain_progress = int((completed_assignments / total_assignments) * 100)
            
        # Calculate Pending Quizzes
        total_quizzes = Quiz.objects.filter(domain=profile.preferred_domain).count()
        taken_quizzes = QuizResult.objects.filter(student=request.user, quiz__domain=profile.preferred_domain).count()
        pending_quizzes = max(0, total_quizzes - taken_quizzes)
    
    recent_achievements = Achievement.objects.all().order_by('-created_at')[:5]
    available_domains = Domain.objects.all()
    
    # Basic community stats
    total_members = User.objects.filter(role='student').count()
    
    # Topic Request
    current_request = TopicRequest.objects.filter(student=request.user, status='PENDING').first()
    topic_form = TopicRequestForm()
    
    return render(request, 'student/dashboard.html', {
        'profile': profile, 
        'recent_achievements': recent_achievements,
        'must_select_domain': must_select_domain,
        'available_domains': available_domains,
        'domain_progress': domain_progress,
        'completed_assignments': completed_assignments,
        'total_assignments': total_assignments,
        'pending_quizzes': pending_quizzes,
        'total_members': total_members,
        'current_request': current_request,
        'topic_form': topic_form,
    })

@login_required
def request_topic(request):
    if request.user.role != 'student': return redirect('home')
    if TopicRequest.objects.filter(student=request.user, status='PENDING').exists():
        messages.warning(request, "You already have a pending topic request.")
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        form = TopicRequestForm(request.POST)
        if form.is_valid():
            topic_req = form.save(commit=False)
            topic_req.student = request.user
            topic_req.save()
            messages.success(request, "Topic request submitted successfully!")
    return redirect('student_dashboard')


@login_required
def student_profile_edit(request):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    # Lock domain once chosen — student cannot change it
    if profile.preferred_domain:
        messages.info(request, f'You are enrolled in "{profile.preferred_domain.name}". Contact your mentor to change domains.')
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.domain_joined_at = timezone.now()
            p.save()
            messages.success(request, f'Successfully enrolled in {p.preferred_domain.name}!')
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'student/profile.html', {'form': form})

@login_required
def leave_domain(request):
    """Student leaves their current domain — account remains approved."""
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    if request.method == 'POST':
        dom_name = profile.preferred_domain.name if profile.preferred_domain else "domain"
        profile.preferred_domain = None
        profile.domain_joined_at = None
        profile.points = 0
        profile.save()
        messages.success(request, f'You have left {dom_name}. Your score has been reset to zero.')
    return redirect('student_domains')

@login_required
def student_domains(request):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    if profile.approval_status != 'APPROVED': return redirect('student_dashboard')
    
    if not profile.preferred_domain:
        messages.warning(request, "Please select a primary track first.")
        return redirect('student_dashboard')
        
    domains = Domain.objects.filter(id=profile.preferred_domain.id)
    return render(request, 'student/domains.html', {'domains': domains})

@login_required
def domain_detail(request, domain_id):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    if profile.approval_status != 'APPROVED': return redirect('student_dashboard')
    
    # Security: Only allow access to their own domain
    if not profile.preferred_domain or profile.preferred_domain.id != domain_id:
        messages.error(request, "Access denied. This is not your assigned domain.")
        return redirect('student_domains')
        
    domain = get_object_or_404(Domain, id=domain_id)
    resources = domain.resources.all()
    assignments = domain.assignments.all()
    return render(request, 'student/domain_detail.html', {'domain': domain, 'resources': resources, 'assignments': assignments})

@login_required
def submit_assignment(request, assignment_id):
    if request.user.role != 'student': return redirect('home')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    status, created = AssignmentStatus.objects.get_or_create(student=request.user, assignment=assignment)
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=status)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.completed = True
            submission.save()
            # Award points
            profile = request.user.student_profile
            profile.points += 50
            profile.save()
            messages.success(request, 'Assignment submitted.')
            return redirect('domain_detail', domain_id=assignment.domain.id)
    else:
        form = AssignmentSubmissionForm(instance=status)
    return render(request, 'student/submit_assignment.html', {'form': form, 'assignment': assignment})

@login_required
def student_quizzes(request):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    if not profile.preferred_domain:
        messages.warning(request, "Select a domain to see relevant quizzes.")
        return redirect('student_dashboard')
        
    quizzes = Quiz.objects.filter(domain=profile.preferred_domain)
    taken_quiz_ids = QuizResult.objects.filter(student=request.user).values_list('quiz_id', flat=True)
    return render(request, 'student/quizzes.html', {
        'quizzes': quizzes, 
        'taken_quiz_ids': taken_quiz_ids
    })

@login_required
def take_quiz(request, quiz_id):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Block retakes
    if QuizResult.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, "You have already taken this quiz.")
        return redirect('student_quizzes')
    
    if quiz.domain != profile.preferred_domain:
        messages.error(request, "You can only take quizzes from your own domain.")
        return redirect('student_quizzes')
    if request.method == 'POST':
        answer = int(request.POST.get('answer'))
        score = 100 if answer == quiz.correct_answer else 0
        QuizResult.objects.create(student=request.user, quiz=quiz, score=score)
        profile = request.user.student_profile
        profile.points += 20
        profile.save()
        return render(request, 'student/quiz_result.html', {'score': score, 'quiz': quiz})
    return render(request, 'student/take_quiz.html', {'quiz': quiz})

@login_required
def achievements_feed(request):
    achievements = Achievement.objects.all().order_by('-created_at')
    liked_achievement_ids = Like.objects.filter(user=request.user).values_list('achievement_id', flat=True)
    return render(request, 'common/achievements.html', {
        'achievements': achievements,
        'liked_achievement_ids': liked_achievement_ids
    })

@login_required
def post_achievement(request):
    if request.user.role != 'student': return redirect('home')
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.student = request.user
            achievement.save()
            profile = request.user.student_profile
            profile.points += 100
            profile.save()
            return redirect('achievements_feed')
    else:
        form = AchievementForm()
    return render(request, 'student/post_achievement.html', {'form': form})

@login_required
def edit_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id, student=request.user)
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES, instance=achievement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Achievement updated successfully.')
            return redirect('achievements_feed')
    else:
        form = AchievementForm(instance=achievement)
    return render(request, 'student/post_achievement.html', {'form': form, 'edit_mode': True})

@login_required
def delete_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id, student=request.user)
    if request.method == 'POST':
        achievement.delete()
        messages.success(request, 'Achievement deleted.')
        return redirect('achievements_feed')
    return render(request, 'student/delete_achievement.html', {'achievement': achievement})

@login_required
def leaderboard(request):
    top_students = StudentProfile.objects.all().order_by('-points')[:10]
    return render(request, 'student/leaderboard.html', {'top_students': top_students})

@login_required
def placement_guide(request):
    resources = PlacementResource.objects.all()
    return render(request, 'student/placement.html', {'resources': resources})

# --- MENTOR ---
@login_required
def mentor_dashboard(request):
    if request.user.role not in ['mentor', 'rep']: return redirect('home')
    # Get students from domains this user is assigned to (as mentor or rep)
    from django.db.models import Q
    my_domains = Domain.objects.filter(Q(mentors=request.user) | Q(student_reps=request.user)).distinct()
    my_students = StudentProfile.objects.filter(preferred_domain__in=my_domains).distinct()

    
    pending_approvals = my_students.filter(approval_status='PENDING')
    approved_students = my_students.filter(approval_status='APPROVED')
    
    # Topic Requests Analytics
    topic_requests = TopicRequest.objects.filter(student__student_profile__preferred_domain__in=my_domains, status='PENDING').order_by('-requested_at')
    from django.db.models import Count, F
    top_domains = TopicRequest.objects.values(domain_name=F('student__student_profile__preferred_domain__name')).annotate(count=Count('id')).order_by('-count')
    
    # Nested distribution: Topics sorted by frequency within each domain
    topic_by_domain = TopicRequest.objects.values(
        domain=F('student__student_profile__preferred_domain__name'),
        topic=F('topic_name')
    ).annotate(count=Count('id')).order_by('domain', '-count')
    
    import json
    # Convert QuerySet to list of dicts for JSON serialization
    topic_distribution_list = list(topic_by_domain)
    topic_distribution_json = json.dumps(topic_distribution_list)
    top_domains_json = json.dumps(list(top_domains))

    total_topic_count = TopicRequest.objects.count()




    
    top_students = StudentProfile.objects.filter(approval_status='APPROVED').order_by('-points')[:5]
    
    return render(request, 'mentor/dashboard.html', {
        'pending_approvals': pending_approvals,
        'my_students': my_students,
        'approved_students': approved_students,
        'my_domains': my_domains,
        'topic_requests': topic_requests,
        'top_topics': top_domains,  # Chart data (Domains)
        'topic_distribution': topic_by_domain, # Detailed breakdown
        'topic_distribution_json': topic_distribution_json,
        'top_domains_json': top_domains_json,
        'total_topic_count': total_topic_count,
        'top_students_global': top_students,
    })




@login_required
def handle_topic_request(request, request_id):
    if request.user.role not in ['mentor', 'rep']: return redirect('home')

    topic_req = get_object_or_404(TopicRequest, id=request_id)
    
    # Security: Ensure user is in the student's domain
    from django.db.models import Q
    if not Domain.objects.filter(Q(mentors=request.user) | Q(student_reps=request.user), id=topic_req.student.student_profile.preferred_domain.id).exists():
        messages.error(request, "Access denied.")
        return redirect('mentor_dashboard')


    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            topic_req.status = 'COMPLETED'
            messages.success(request, f"Topic '{topic_req.topic_name}' marked as completed.")
        elif action == 'reject':
            topic_req.status = 'REJECTED'
            messages.success(request, f"Topic '{topic_req.topic_name}' rejected.")
        elif action == 'reset':
            # Option to delete or mark as reset so they can request again
            topic_req.status = 'COMPLETED' # Assuming reset means they can request again, COMPLETED also allows it if we filter by PENDING
            messages.success(request, "Request reset.")
        topic_req.save()
        
    return redirect('mentor_dashboard')

@login_required
def reset_domain_topics(request, domain_id):
    if request.user.role not in ['mentor', 'rep']: return redirect('home')
    from django.db.models import Q
    domain = get_object_or_404(Domain, Q(id=domain_id), Q(mentors=request.user) | Q(student_reps=request.user))

    
    if request.method == 'POST':
        # Reset (delete) all topic requests for students in this domain to allow new ones
        deleted_count, _ = TopicRequest.objects.filter(
            student__student_profile__preferred_domain=domain
        ).delete()
        messages.success(request, f"Successfully reset {deleted_count} topic requests for {domain.name}. Students can now request again.")
        
    return redirect('mentor_dashboard')


@login_required
def mentor_students(request):
    if request.user.role != 'mentor': return redirect('home')
    # Get students from domains this user is assigned to
    from django.db.models import Q
    my_domains = Domain.objects.filter(Q(mentors=request.user) | Q(student_reps=request.user)).distinct()
    students = StudentProfile.objects.filter(
        preferred_domain__in=my_domains,
        user__role__in=['student', 'alumni']
    ).distinct()
    return render(request, 'mentor/students.html', {'students': students})



@login_required
def mentor_quick_approve(request, profile_id):
    if request.user.role == 'rep':
        messages.error(request, "Student Representatives cannot approve applications.")
        return redirect('mentor_dashboard')
    if request.user.role != 'mentor': return redirect('home')
    profile = get_object_or_404(StudentProfile, id=profile_id, preferred_domain__mentors=request.user)
    if request.method == 'POST':

        profile.approval_status = 'APPROVED'
        profile.approved_at = timezone.now()
        profile.save()
        messages.success(request, f'Student {profile.user.username} has been granted access.')
    return redirect('mentor_dashboard')

@login_required
def mentor_domains(request):
    if request.user.role not in ['mentor', 'rep']: return redirect('home')
    # Users see domains they are assigned to
    from django.db.models import Q
    domains = Domain.objects.filter(Q(mentors=request.user) | Q(student_reps=request.user)).distinct()
    return render(request, 'mentor/domains.html', {'domains': domains})


@login_required
def mentor_edit_domain(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    # Security: Mentor/Rep must be assigned OR be HOD
    from django.db.models import Q
    if request.user.role != 'hod' and not Domain.objects.filter(Q(mentors=request.user) | Q(student_reps=request.user), id=domain_id).exists():
        messages.error(request, "Access denied. You are not assigned to this domain.")
        return redirect('mentor_domains')
    
    # reps shouldn't edit domain metadata
    if request.user.role == 'rep':
        messages.error(request, "Student Representatives cannot edit domain metadata.")
        return redirect('mentor_domains')

    if request.method == 'POST':
        form = DomainForm(request.POST, instance=domain)
        if form.is_valid():
            form.save()
            messages.success(request, f'Domain "{domain.name}" updated successfully.')
            return redirect('mentor_domains')
    else:
        form = DomainForm(instance=domain)
    return render(request, 'mentor/edit_domain.html', {'form': form, 'domain': domain})

@login_required
def mentor_delete_domain(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    # Security: Only HOD or Domain Creator can delete
    if request.user.role != 'hod' and domain.created_by != request.user:
        messages.error(request, "Access denied. Only HOD or the Domain Creator can delete the domain.")
        return redirect('mentor_domains')
    
    if request.method == 'POST':
        dom_name = domain.name
        domain.delete()
        messages.warning(request, f'Domain "{dom_name}" has been permanently removed.')
        return redirect('mentor_domains')
    return render(request, 'mentor/confirm_delete_domain.html', {'domain': domain})


@login_required
def hod_add_domain(request):
    if request.user.role != 'hod': return redirect('home')
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            domain = form.save(commit=False)
            domain.created_by = request.user
            domain.save()
            messages.success(request, f'Domain "{domain.name}" created successfully.')
            return redirect('hod_domains')
    else:
        form = DomainForm()
    return render(request, 'hod/add_domain.html', {'form': form})

@login_required

@login_required
def add_resource(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    # Security: Only creator (HOD/Mentor) OR assigned mentors can add resources
    if domain.created_by != request.user and request.user not in domain.mentors.all():
        messages.error(request, "Access denied. You are not assigned to this domain.")
        return redirect('mentor_dashboard')
        
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.domain = domain
            resource.save()
            return redirect('mentor_domain_curriculum', domain_id=domain.id)
    else:
        form = ResourceForm()
    return render(request, 'mentor/add_resource.html', {'form': form, 'domain': domain})

@login_required
def add_assignment(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    # Security: Only creator (HOD/Mentor) OR assigned mentors can add assignments
    if domain.created_by != request.user and request.user not in domain.mentors.all():
        messages.error(request, "Access denied. You are not assigned to this domain.")
        return redirect('mentor_dashboard')
        
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.domain = domain
            assignment.save()
            return redirect('mentor_domain_curriculum', domain_id=domain.id)
    else:
        form = AssignmentForm()
    return render(request, 'mentor/add_assignment.html', {'form': form, 'domain': domain})

@login_required
def mentor_domain_curriculum(request, domain_id):

    domain = get_object_or_404(Domain, id=domain_id)
    # Security: Mentor/Rep must be assigned
    from django.db.models import Q
    if request.user.role != 'hod' and not Domain.objects.filter(Q(mentors=request.user) | Q(student_reps=request.user), id=domain_id).exists():
        messages.error(request, "Access denied. You are not assigned to this domain.")
        return redirect('mentor_domains')
    
    resources = domain.resources.all().order_by('-id')
    assignments = domain.assignments.all().order_by('-due_date')
    
    return render(request, 'mentor/domain_curriculum.html', {
        'domain': domain,
        'resources': resources,
        'assignments': assignments,
    })

@login_required
def mentor_edit_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    domain = resource.domain
    # Security
    if request.user.role != 'hod' and request.user not in domain.mentors.all():
        messages.error(request, "Access denied.")
        return redirect('mentor_domains')
        
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource updated successfully.")
            return redirect('mentor_domain_curriculum', domain_id=domain.id)
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'mentor/edit_resource.html', {'form': form, 'resource': resource, 'domain': domain})

@login_required
def mentor_delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    domain = resource.domain
    # Security
    if request.user.role != 'hod' and request.user not in domain.mentors.all():
        messages.error(request, "Access denied.")
        return redirect('mentor_domains')
        
    if request.method == 'POST':
        resource.delete()
        messages.warning(request, "Resource has been removed.")
    return redirect('mentor_domain_curriculum', domain_id=domain.id)

@login_required
def mentor_edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    domain = assignment.domain
    # Security
    if request.user.role != 'hod' and request.user not in domain.mentors.all():
        messages.error(request, "Access denied.")
        return redirect('mentor_domains')
        
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('mentor_domain_curriculum', domain_id=domain.id)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'mentor/edit_assignment.html', {'form': form, 'assignment': assignment, 'domain': domain})

@login_required
def mentor_delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    domain = assignment.domain
    # Security
    if request.user.role != 'hod' and request.user not in domain.mentors.all():
        messages.error(request, "Access denied.")
        return redirect('mentor_domains')
        
    if request.method == 'POST':
        assignment.delete()
        messages.warning(request, "Task has been removed.")
    return redirect('mentor_domain_curriculum', domain_id=domain.id)


@login_required
def grade_submissions(request):
    if request.user.role != 'mentor': return redirect('home')
    submissions = AssignmentStatus.objects.filter(assignment__domain__created_by=request.user, completed=True, mentor_score__isnull=True)
    return render(request, 'mentor/grade_submissions.html', {'submissions': submissions})

@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(AssignmentStatus, id=submission_id, assignment__domain__created_by=request.user)
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('grade_submissions')
    else:
        form = GradeSubmissionForm(instance=submission)
    return render(request, 'mentor/grade_one.html', {'form': form, 'submission': submission})

# --- HOD ---
@login_required
def hod_dashboard(request):
    if request.user.role != 'hod': return redirect('home')
    total_students = User.objects.filter(role='student').count()
    total_mentors = User.objects.filter(role='mentor').count()
    total_domains = Domain.objects.count()
    pending_approvals = StudentProfile.objects.filter(approval_status__in=['PENDING', 'MENTOR_APPROVED']).count()
    top_students = StudentProfile.objects.filter(approval_status='APPROVED').order_by('-points')[:5]
    return render(request, 'hod/dashboard.html', {
        'total_students': total_students,
        'total_mentors': total_mentors,
        'total_domains': total_domains,
        'pending_approvals': pending_approvals,
        'top_students': top_students,
    })


@login_required
def hod_approve_student(request, profile_id):
    """HOD gives final approval to access the website."""
    if request.user.role != 'hod': return redirect('home')
    profile = get_object_or_404(StudentProfile, id=profile_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            profile.approval_status = 'APPROVED'
            profile.approved_at = timezone.now()
            messages.success(request, f'{profile.user.username} has been granted platform access.')
        else:
            profile.approval_status = 'REJECTED'
            profile.approval_remark = request.POST.get('remark', 'Rejected by HOD.')
            messages.warning(request, f'{profile.user.username} account creation rejected.')
        profile.save()
    return redirect('hod_users')

@login_required
def hod_users(request):
    if request.user.role != 'hod': return redirect('home')
    
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if query:
        users = users.filter(
            models.Q(username__icontains=query) | 
            models.Q(email__icontains=query)
        )
        
    if role_filter:
        users = users.filter(role=role_filter)
        
    return render(request, 'hod/users.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter
    })

@login_required
def hod_toggle_user(request, user_id):
    if request.user.role != 'hod': return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('hod_users')

@login_required
def hod_change_role(request, user_id):
    if request.user.role != 'hod': return redirect('home')
    user = get_object_or_404(User, id=user_id)
    new_role = request.GET.get('role')
    
    # Security: Don't allow changing HOD roles through this simple toggle
    if user.role == 'hod' or new_role == 'hod':
        messages.error(request, "HOD roles cannot be modified via this shortcut.")
        return redirect('hod_users')

    if new_role in [choice[0] for choice in User.ROLE_CHOICES]:
        old_role = user.role
        user.role = new_role
        user.save()
        
        # Ensure StudentProfile exists if becoming a student
        if new_role == 'student':
            from .models import StudentProfile
            StudentProfile.objects.get_or_create(user=user)
            messages.success(request, f'Access revoked. {user.username} is now a Student.')
        
        # If they were a student and are now a mentor or rep
        elif old_role == 'student' and new_role in ['mentor', 'rep']:
            user.is_active = True
            user.save()
            messages.success(request, f'Promotion successful. {user.username} is now a {user.get_role_display()}.')
        else:
            messages.success(request, f'User {user.username} role updated to {user.get_role_display()}.')

    
    return redirect('hod_users')

@login_required
def hod_graduate_student(request, user_id):
    # Allow HOD and Mentors to graduate
    if request.user.role not in ['hod', 'mentor']:
        return redirect('home')
        
    student_user = get_object_or_404(User, id=user_id)
    
    if student_user.role == 'alumni':
        messages.info(request, f"{student_user.username} is already an Alumni.")
        return redirect('hod_users' if request.user.role == 'hod' else 'mentor_students')
        
    if student_user.role != 'student':
        messages.error(request, "Only students can be graduated.")
        return redirect('hod_users' if request.user.role == 'hod' else 'mentor_students')

    profile = student_user.student_profile
    
    # Security: Mentors can only graduate students in their domains
    if request.user.role == 'mentor':
        if not Domain.objects.filter(mentors=request.user, id=profile.preferred_domain.id).exists():
            messages.error(request, "Access denied. You can only graduate students in your assigned domains.")
            return redirect('mentor_students')

    if request.method == 'POST':
        grad_year = request.POST.get('graduation_year')
        company = request.POST.get('current_company')
        description = request.POST.get('description', '')
        
        # Create Alumni record
        Alumni.objects.create(
            user=student_user,
            name=f"{student_user.first_name} {student_user.last_name}" if (student_user.first_name or student_user.last_name) else student_user.username,
            graduation_year=grad_year,
            current_company=company,
            domain=profile.preferred_domain,
            profile_description=description
        )
        
        # Change user role
        student_user.role = 'alumni'
        student_user.save()
        
        messages.success(request, f"Congratulations! {student_user.username} has been graduated to Alumni.")
    
    return redirect('hod_users' if request.user.role == 'hod' else 'mentor_students')

@login_required
def update_alumni_profile(request, user_id):
    if request.user.role not in ['hod', 'mentor']:
        return redirect('home')
        
    alumni_user = get_object_or_404(User, id=user_id, role='alumni')
    alumni_profile = get_object_or_404(Alumni, user=alumni_user)
    
    if request.user.role == 'mentor':
        if not Domain.objects.filter(mentors=request.user, id=alumni_profile.domain.id).exists():
            messages.error(request, "Access denied. You can only edit alumni in your assigned domains.")
            return redirect('mentor_students')

    if request.method == 'POST':
        alumni_profile.graduation_year = request.POST.get('graduation_year')
        alumni_profile.current_company = request.POST.get('current_company')
        alumni_profile.profile_description = request.POST.get('description', '')
        alumni_profile.save()
        
        messages.success(request, f"Profile for {alumni_user.username} updated successfully.")
        
    return redirect('hod_users' if request.user.role == 'hod' else 'mentor_students')


@login_required
def hod_feedback(request):
    if request.user.role != 'hod': return redirect('home')
    feedbacks = Feedback.objects.all()
    return render(request, 'hod/feedback.html', {'feedbacks': feedbacks})

@login_required
def hod_domains(request):
    if request.user.role != 'hod': return redirect('home')
    domains = Domain.objects.all()
    return render(request, 'hod/domains.html', {'domains': domains})

@login_required
def hod_allocate_mentors(request, domain_id):
    if request.user.role != 'hod': return redirect('home')
    domain = get_object_or_404(Domain, id=domain_id)
    if request.method == 'POST':
        mentor_ids = request.POST.getlist('mentor_ids')
        rep_ids = request.POST.getlist('rep_ids')
        domain.mentors.set(User.objects.filter(id__in=mentor_ids))
        domain.student_reps.set(User.objects.filter(id__in=rep_ids))
        messages.success(request, f'Assignment updated for {domain.name}')
        return redirect('hod_domains')
    all_mentors = User.objects.filter(role='mentor')
    all_reps = User.objects.filter(role='rep')
    selected_mentor_ids = list(domain.mentors.values_list('id', flat=True))
    selected_rep_ids = list(domain.student_reps.values_list('id', flat=True))
    return render(request, 'hod/allocate_mentors.html', {
        'domain': domain, 
        'all_mentors': all_mentors,
        'all_reps': all_reps,
        'selected_mentor_ids': selected_mentor_ids,
        'selected_rep_ids': selected_rep_ids
    })


# --- ALUMNI ---
@login_required
def alumni_profile(request, user_id):

    alumni_user = get_object_or_404(User, id=user_id, role='alumni')
    profile = get_object_or_404(Alumni, user=alumni_user)
    posts = Post.objects.filter(alumni=profile).order_by('-created_at')
    return render(request, 'alumni/profile.html', {
        'alumni_user': alumni_user,
        'profile': profile,
        'posts': posts
    })

def alumni_posts(request):

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'alumni/posts.html', {'posts': posts})

@login_required
def add_alumni_post(request):
    # Allow HOD and Mentors to add posts, or anyone for now if role checking is not strictly required
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumni insight posted successfully.')
            return redirect('alumni_posts')
    else:
        form = PostForm()
    return render(request, 'alumni/add_post.html', {'form': form})

@login_required
def add_alumni(request):
    if request.user.role not in ['hod', 'mentor']:
        messages.error(request, "Only HODs and Mentors can manage alumni profiles.")
        return redirect('alumni_posts')
        
    if request.method == 'POST':
        form = AlumniForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumni profile created successfully.')
            return redirect('add_alumni_post')
    else:
        form = AlumniForm()
    return render(request, 'alumni/add_alumni.html', {'form': form})

# --- FEEDBACK ---
@login_required
def submit_feedback(request):
    if request.user.role != 'student': return redirect('home')
    
    student_profile = request.user.student_profile
    student_domain = student_profile.preferred_domain
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        # Re-apply filters for validation
        if student_domain:
            form.fields['domain'].queryset = Domain.objects.filter(id=student_domain.id)
            form.fields['mentor'].queryset = User.objects.filter(role='mentor', allocated_domains=student_domain)
        
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('student_dashboard')
    else:
        # Pre-fill domain if student has one
        initial_data = {}
        if student_domain:
            initial_data['domain'] = student_domain
        
        form = FeedbackForm(initial=initial_data)
        
        # Filter choices
        if student_domain:
            form.fields['domain'].queryset = Domain.objects.filter(id=student_domain.id)
            form.fields['mentor'].queryset = User.objects.filter(role='mentor', allocated_domains=student_domain)
        else:
            # If no domain yet, maybe show all but it's better to show empty or all
            pass

    return render(request, 'student/feedback.html', {'form': form, 'student_domain': student_domain})

@login_required
def like_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id)
    like_qs = Like.objects.filter(achievement=achievement, user=request.user)
    if like_qs.exists():
        like_qs.delete()
    else:
        Like.objects.create(achievement=achievement, user=request.user)
    return redirect('achievements_feed')

@login_required
def add_comment(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(achievement=achievement, user=request.user, content=content)
    return redirect('achievements_feed')

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
    return redirect('achievements_feed')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return redirect('achievements_feed')
