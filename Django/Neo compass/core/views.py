from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, StudentProfileForm, DomainForm, ResourceForm, AssignmentForm, AssignmentSubmissionForm, GradeSubmissionForm, QuizForm, AchievementForm, FeedbackForm
from .models import User, StudentProfile, Domain, Resource, Assignment, AssignmentStatus, Quiz, QuizResult, PlacementResource, Alumni, Post, Achievement, Like, Comment, Feedback
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
    elif request.user.role == 'mentor':
        return redirect('mentor_dashboard')
    elif request.user.role == 'hod':
        return redirect('hod_dashboard')
    return redirect('login')

# --- STUDENT ---
@login_required
def student_dashboard(request):
    if request.user.role != 'student': return redirect('home')
    profile = request.user.student_profile
    if profile.approval_status != 'APPROVED':
        return render(request, 'student/pending.html', {'profile': profile})
    
    must_select_domain = profile.preferred_domain is None
    
    recent_achievements = Achievement.objects.all().order_by('-created_at')[:5]
    available_domains = Domain.objects.all()
    return render(request, 'student/dashboard.html', {
        'profile': profile, 
        'recent_achievements': recent_achievements,
        'must_select_domain': must_select_domain,
        'available_domains': available_domains
    })

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
    if request.user.role != 'mentor': return redirect('home')
    my_students = StudentProfile.objects.filter(assigned_mentor=request.user)
    pending_approvals = my_students.filter(approval_status='PENDING')
    approved_students = my_students.filter(approval_status='APPROVED')
    my_domains = Domain.objects.filter(mentors=request.user)
    return render(request, 'mentor/dashboard.html', {
        'pending_approvals': pending_approvals,
        'my_students': my_students,
        'approved_students': approved_students,
        'my_domains': my_domains,
    })

@login_required
def mentor_students(request):
    if request.user.role != 'mentor': return redirect('home')
    students = StudentProfile.objects.filter(assigned_mentor=request.user)
    return render(request, 'mentor/students.html', {'students': students})

@login_required
def approve_student(request, profile_id):
    if request.user.role != 'mentor': return redirect('home')
    profile = get_object_or_404(StudentProfile, id=profile_id, assigned_mentor=request.user)
    if request.method == 'POST':
        action = request.POST.get('status')
        remark = request.POST.get('remark', '')
        profile.approval_remark = remark
        if action == 'APPROVED':
            profile.approval_status = 'APPROVED'
            profile.approved_at = timezone.now()
            messages.success(request, f'Student {profile.user.username} approved to access the platform.')
        else:
            profile.approval_status = 'REJECTED'
            messages.warning(request, f'Student {profile.user.username} rejected.')
        profile.save()
        return redirect('mentor_dashboard')
    return render(request, 'mentor/approve_student.html', {'profile': profile})

@login_required
def mentor_domains(request):
    if request.user.role != 'mentor': return redirect('home')
    domains = Domain.objects.filter(created_by=request.user)
    return render(request, 'mentor/domains.html', {'domains': domains})

@login_required
def add_domain(request):
    if request.user.role != 'mentor': return redirect('home')
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            domain = form.save(commit=False)
            domain.created_by = request.user
            domain.save()
            return redirect('mentor_domains')
    else:
        form = DomainForm()
    return render(request, 'mentor/add_domain.html', {'form': form})

@login_required
def add_resource(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, created_by=request.user)
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.domain = domain
            resource.save()
            return redirect('mentor_domains')
    else:
        form = ResourceForm()
    return render(request, 'mentor/add_resource.html', {'form': form, 'domain': domain})

@login_required
def add_assignment(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, created_by=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.domain = domain
            assignment.save()
            return redirect('mentor_domains')
    else:
        form = AssignmentForm()
    return render(request, 'mentor/add_assignment.html', {'form': form, 'domain': domain})

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
    return render(request, 'hod/dashboard.html', {
        'total_students': total_students,
        'total_mentors': total_mentors,
        'total_domains': total_domains,
        'pending_approvals': pending_approvals
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
    users = User.objects.all()
    return render(request, 'hod/users.html', {'users': users})

@login_required
def hod_toggle_user(request, user_id):
    if request.user.role != 'hod': return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('hod_users')

@login_required
def assign_mentor(request, profile_id):
    if request.user.role != 'hod': return redirect('home')
    profile = get_object_or_404(StudentProfile, id=profile_id)
    if profile.preferred_domain:
        mentors = profile.preferred_domain.mentors.all()
        if not mentors.exists():
            mentors = User.objects.filter(role='mentor')
    else:
        mentors = User.objects.filter(role='mentor')
    if request.method == 'POST':
        mentor_id = request.POST.get('mentor_id')
        profile.assigned_mentor = get_object_or_404(User, id=mentor_id)
        profile.save()
        messages.success(request, f'Mentor assigned to {profile.user.username}')
        return redirect('hod_users')
    return render(request, 'hod/assign_mentor.html', {'profile': profile, 'mentors': mentors})

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
        domain.mentors.set(User.objects.filter(id__in=mentor_ids))
        messages.success(request, f'Mentors updated for {domain.name}')
        return redirect('hod_domains')
    all_mentors = User.objects.filter(role='mentor')
    return render(request, 'hod/allocate_mentors.html', {'domain': domain, 'all_mentors': all_mentors})

# --- ALUMNI ---
@login_required
def alumni_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'alumni/posts.html', {'posts': posts})

# --- FEEDBACK ---
@login_required
def submit_feedback(request):
    if request.user.role != 'student': return redirect('home')
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.save()
            return redirect('student_dashboard')
    else:
        form = FeedbackForm()
    return render(request, 'student/feedback.html', {'form': form})

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
