from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Donation
from .forms import DonationForm, AssignVolunteerForm
from accounts.models import CustomUser
from tracking.models import StatusHistory

# ============= DONOR VIEWS =============

@login_required
def donor_dashboard(request):
    """Donor dashboard showing their donations"""
    donations = Donation.objects.filter(donor=request.user).order_by('-created_at')
    pending_count = donations.filter(status='Pending').count()
    accepted_count = donations.filter(status='Accepted').count()
    delivered_count = donations.filter(status='Delivered').count()
    
    return render(request, 'donations/donor_dashboard.html', {
        'donations': donations,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'delivered_count': delivered_count,
    })

@login_required
def create_donation(request):
    """Create a new donation"""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            
            # Create status history
            StatusHistory.objects.create(
                donation=donation,
                status='Pending',
                changed_by=request.user,
                notes='Donation created'
            )
            
            messages.success(request, "Donation created successfully! Thank you for your contribution.")
            return redirect('donor_dashboard')
        else:
            messages.error(request, "There was an error with your donation. Please check the details.")
    else:
        form = DonationForm()
    return render(request, 'donations/create_donation.html', {'form': form})

@login_required
def donation_detail(request, donation_id):
    """View donation details with status history"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Check permissions
    if request.user.role == 'donor' and donation.donor != request.user:
        messages.error(request, "You don't have permission to view this donation.")
        return redirect('donor_dashboard')
    
    status_history = donation.status_history.all()
    
    return render(request, 'donations/donation_detail.html', {
        'donation': donation,
        'status_history': status_history
    })

# ============= NGO VIEWS =============

@login_required
def ngo_dashboard(request):
    """NGO dashboard showing pending and accepted donations with distances"""
    if request.user.role != 'ngo':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    pending_donations = Donation.objects.filter(status='Pending').order_by('-created_at')
    accepted_donations = Donation.objects.filter(
        assigned_ngo=request.user,
        status__in=['Accepted', 'Picked', 'Delivered']
    ).order_by('-updated_at')
    
    # Calculate distances for pending donations if NGO has location set
    pending_with_distance = []
    if request.user.latitude and request.user.longitude:
        for donation in pending_donations:
            distance = donation.calculate_distance(
                float(request.user.latitude),
                float(request.user.longitude)
            )
            can_accept = distance is None or distance <= 20  # 20km limit
            pending_with_distance.append({
                'donation': donation,
                'distance': distance,
                'can_accept': can_accept
            })
    else:
        for donation in pending_donations:
            pending_with_distance.append({
                'donation': donation,
                'distance': None,
                'can_accept': False  # Must set location first
            })
    
    return render(request, 'donations/ngo_dashboard.html', {
        'pending_with_distance': pending_with_distance,
        'accepted_donations': accepted_donations,
    })


@login_required
def accept_donation(request, donation_id):
    """NGO accepts a donation with distance check"""
    if request.user.role != 'ngo':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donation = get_object_or_404(Donation, id=donation_id)
    
    if donation.status != 'Pending':
        messages.error(request, "This donation is no longer pending.")
        return redirect('ngo_dashboard')
    
    # Check NGO location and distance (20km limit)
    if not request.user.latitude or not request.user.longitude:
        messages.error(request, "Please set your location before accepting donations.")
        return redirect('update_location')
    
    if donation.latitude and donation.longitude:
        distance = donation.calculate_distance(
            float(request.user.latitude),
            float(request.user.longitude)
        )
        
        if distance and distance > 20:
            messages.error(request, 
                f"Cannot accept donation. Pickup location is {distance} km away (maximum allowed: 20 km). "
                "Please set your location closer to the donation or choose a nearer donation.")
            return redirect('ngo_dashboard')
    
    donation.status = 'Accepted'
    donation.assigned_ngo = request.user
    donation.save()
    
    # Create status history
    StatusHistory.objects.create(
        donation=donation,
        status='Accepted',
        changed_by=request.user,
        notes=f'Accepted by NGO: {request.user.username}'
    )
    
    messages.success(request, f"Donation #{donation.id} accepted successfully!")
    return redirect('ngo_dashboard')

@login_required
def reject_donation(request, donation_id):
    """NGO rejects a donation"""
    if request.user.role != 'ngo':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donation = get_object_or_404(Donation, id=donation_id)
    
    if donation.status != 'Pending':
        messages.error(request, "This donation is no longer pending.")
        return redirect('ngo_dashboard')
    
    donation.status = 'Rejected'
    donation.save()
    
    # Create status history
    StatusHistory.objects.create(
        donation=donation,
        status='Rejected',
        changed_by=request.user,
        notes=f'Rejected by NGO: {request.user.username}'
    )
    
    messages.warning(request, f"Donation #{donation.id} has been rejected.")
    return redirect('ngo_dashboard')

@login_required
def cancel_acceptance(request, donation_id):
    """NGO cancels their acceptance of a donation (before volunteer is assigned)"""
    if request.user.role != 'ngo':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donation = get_object_or_404(Donation, id=donation_id, assigned_ngo=request.user)
    
    if donation.status != 'Accepted':
        messages.error(request, "Cannot cancel this donation. It may already be in progress.")
        return redirect('ngo_dashboard')
    
    if donation.assigned_volunteer:
        messages.error(request, "Cannot cancel as a volunteer has already been assigned.")
        return redirect('ngo_dashboard')
    
    donation.status = 'Pending'
    donation.assigned_ngo = None
    donation.save()
    
    # Create status history
    StatusHistory.objects.create(
        donation=donation,
        status='Pending',
        changed_by=request.user,
        notes=f'Acceptance cancelled by NGO: {request.user.username}. It is now open for others.'
    )
    
    messages.info(request, f"Donation #{donation.id} has been released and is now back in pending status.")
    return redirect('ngo_dashboard')

@login_required
def assign_volunteer(request, donation_id):
    """NGO assigns a volunteer to a donation with distance info"""
    if request.user.role != 'ngo':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donation = get_object_or_404(Donation, id=donation_id, assigned_ngo=request.user)
    
    if donation.status not in ['Accepted']:
        messages.error(request, "Cannot assign volunteer to this donation.")
        return redirect('ngo_dashboard')
    
    if request.method == 'POST':
        volunteer_id = request.POST.get('volunteer')
        if volunteer_id:
            try:
                volunteer = CustomUser.objects.get(id=volunteer_id, role='volunteer', is_approved=True)
                donation.assigned_volunteer = volunteer
                donation.save()
                
                # Create status history
                StatusHistory.objects.create(
                    donation=donation,
                    status='Accepted',
                    changed_by=request.user,
                    notes=f'Volunteer assigned: {volunteer.username}'
                )
                
                messages.success(request, f"Volunteer {volunteer.username} assigned successfully!")
                return redirect('ngo_dashboard')
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid volunteer selected.")
        else:
            messages.error(request, "Please select a volunteer.")
    
    # Calculate distances for all volunteers
    volunteers_with_distance = []
    all_volunteers = CustomUser.objects.filter(role='volunteer', is_approved=True)
    
    for volunteer in all_volunteers:
        if volunteer.latitude and volunteer.longitude and donation.latitude and donation.longitude:
            distance = donation.calculate_distance(
                float(volunteer.latitude),
                float(volunteer.longitude)
            )
        else:
            distance = None
        
        volunteers_with_distance.append({
            'volunteer': volunteer,
            'distance': distance,
            'has_location': volunteer.latitude is not None and volunteer.longitude is not None
        })
    
    # Sort by distance (volunteers with location first, then by distance)
    volunteers_with_distance.sort(key=lambda x: (
        not x['has_location'],  # Volunteers without location go last
        x['distance'] if x['distance'] is not None else float('inf')  # Then sort by distance
    ))
    
    return render(request, 'donations/assign_volunteer.html', {
        'donation': donation,
        'volunteers_with_distance': volunteers_with_distance
    })



# ============= VOLUNTEER VIEWS =============

@login_required
def volunteer_dashboard(request):
    """Volunteer dashboard showing assigned pickups with distances"""
    if request.user.role != 'volunteer':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    assigned_donations = Donation.objects.filter(
        assigned_volunteer=request.user
    ).exclude(status='Delivered').order_by('-updated_at')
    
    completed_donations = Donation.objects.filter(
        assigned_volunteer=request.user,
        status='Delivered'
    ).order_by('-updated_at')[:10]
    
    # Calculate distances if volunteer has location set
    donations_with_distance = []
    if request.user.latitude and request.user.longitude:
        for donation in assigned_donations:
            distance = donation.calculate_distance(
                float(request.user.latitude),
                float(request.user.longitude)
            )
            donations_with_distance.append({
                'donation': donation,
                'distance': distance
            })
    else:
        for donation in assigned_donations:
            donations_with_distance.append({
                'donation': donation,
                'distance': None
            })
    
    return render(request, 'donations/volunteer_dashboard.html', {
        'donations_with_distance': donations_with_distance,
        'completed_donations': completed_donations,
    })


@login_required
def mark_picked(request, donation_id):
    """Volunteer marks donation as picked with distance and OTP check"""
    if request.user.role != 'volunteer':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donation = get_object_or_404(Donation, id=donation_id, assigned_volunteer=request.user)
    
    if donation.status != 'Accepted':
        messages.error(request, "This donation cannot be marked as picked.")
        return redirect('volunteer_dashboard')

    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == donation.pickup_otp:
            # Check volunteer location and distance (15km limit)
            if not request.user.latitude or not request.user.longitude:
                messages.error(request, "Please set your location before picking up donations.")
                return redirect('update_location')
            
            if donation.latitude and donation.longitude:
                distance = donation.calculate_distance(
                    float(request.user.latitude),
                    float(request.user.longitude)
                )
                
                if distance and distance > 15:
                    messages.error(request, 
                        f"Cannot pick up donation. Pickup location is {distance} km away (maximum allowed: 15 km).")
                    return redirect('volunteer_dashboard')
            
            donation.status = 'Picked'
            donation.save()
            
            # Create status history
            StatusHistory.objects.create(
                donation=donation,
                status='Picked',
                changed_by=request.user,
                notes=f'Picked up by volunteer: {request.user.username} (OTP Verified)'
            )
            
            messages.success(request, f"Donation #{donation.id} marked as picked!")
            return redirect('volunteer_dashboard')
        else:
            messages.error(request, "Invalid Pickup OTP. Please ask the donor for the correct code.")
            return render(request, 'donations/verify_otp.html', {
                'donation': donation,
                'type': 'Pickup',
                'description': 'Enter the 6-digit OTP provided by the Donor to confirm pickup.'
            })

    return render(request, 'donations/verify_otp.html', {
        'donation': donation,
        'type': 'Pickup',
        'description': 'Enter the 6-digit OTP provided by the Donor to confirm pickup.'
    })



@login_required
def mark_delivered(request, donation_id):
    """Volunteer or NGO marks donation as delivered with OTP check for volunteers"""
    if request.user.role not in ['volunteer', 'ngo']:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    if request.user.role == 'volunteer':
        donation = get_object_or_404(Donation, id=donation_id, assigned_volunteer=request.user)
        
        if donation.status != 'Picked':
            messages.error(request, "This donation must be picked before delivery.")
            return redirect('volunteer_dashboard')

        if request.method == 'POST':
            otp = request.POST.get('otp')
            if otp == donation.delivery_otp:
                donation.status = 'Delivered'
                donation.save()
                
                StatusHistory.objects.create(
                    donation=donation,
                    status='Delivered',
                    changed_by=request.user,
                    notes=f'Delivered by volunteer: {request.user.username} (OTP Verified)'
                )
                messages.success(request, f"Donation #{donation.id} marked as delivered!")
                return redirect('volunteer_dashboard')
            else:
                messages.error(request, "Invalid Delivery OTP. Please ask the NGO for the correct code.")
                return render(request, 'donations/verify_otp.html', {
                    'donation': donation,
                    'type': 'Delivery',
                    'description': 'Enter the 6-digit OTP provided by the NGO to confirm delivery.'
                })
        
        return render(request, 'donations/verify_otp.html', {
            'donation': donation,
            'type': 'Delivery',
            'description': 'Enter the 6-digit OTP provided by the NGO to confirm delivery.'
        })

    else: # NGO
        donation = get_object_or_404(Donation, id=donation_id, assigned_ngo=request.user)
        if donation.status not in ['Picked', 'Accepted']:
            messages.error(request, "This donation cannot be marked as delivered in its current state.")
            return redirect('ngo_dashboard')
        
        donation.status = 'Delivered'
        donation.save()
        
        StatusHistory.objects.create(
            donation=donation,
            status='Delivered',
            changed_by=request.user,
            notes=f'Delivered marked by NGO: {request.user.username}'
        )
        messages.success(request, f"Donation #{donation.id} marked as delivered!")
        return redirect('ngo_dashboard')



# ============= ADMIN VIEWS =============

@login_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    total_donations = Donation.objects.count()
    pending_donations = Donation.objects.filter(status='Pending').count()
    delivered_donations = Donation.objects.filter(status='Delivered').count()
    total_users = CustomUser.objects.count()
    pending_users = CustomUser.objects.filter(is_approved=False).count()
    
    recent_donations = Donation.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'donations/admin_dashboard.html', {
        'total_donations': total_donations,
        'pending_donations': pending_donations,
        'delivered_donations': delivered_donations,
        'total_users': total_users,
        'pending_users': pending_users,
        'recent_donations': recent_donations,
    })

@login_required
def manage_users(request):
    """Admin view to manage all users"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(phone_number__icontains=search_query)
        )
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filter by approval status
    approval_filter = request.GET.get('approval', '')
    if approval_filter == 'approved':
        users = users.filter(is_approved=True)
    elif approval_filter == 'pending':
        users = users.filter(is_approved=False)
    
    return render(request, 'donations/manage_users.html', {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'approval_filter': approval_filter,
    })

@login_required
def toggle_user_status(request, user_id):
    """Admin activates or deactivates a user"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    if user.id == request.user.id:
        messages.error(request, "You cannot deactivate yourself.")
        return redirect('manage_users')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect('manage_users')

@login_required
def approve_user(request, user_id):
    """Admin approves a user"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    
    messages.success(request, f"User {user.username} has been approved.")
    return redirect('manage_users')

@login_required
def manage_donations(request):
    """Admin view to manage all donations"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donations = Donation.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        donations = donations.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        donations = donations.filter(
            Q(food_type__icontains=search_query) |
            Q(donor__username__icontains=search_query)
        )
    
    return render(request, 'donations/manage_donations.html', {
        'donations': donations,
        'status_filter': status_filter,
        'search_query': search_query,
    })

@login_required
def delete_donation(request, donation_id):
    """Admin deletes a donation"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    donation = get_object_or_404(Donation, id=donation_id)
    donation_info = f"#{donation.id} - {donation.food_type}"
    donation.delete()
    
    messages.success(request, f"Donation {donation_info} has been deleted.")
    return redirect('manage_donations')

# ============= GENERAL VIEWS =============

@login_required
def donation_list(request):
    """List all donations (accessible to all authenticated users)"""
    donations = Donation.objects.all().order_by('-created_at')
    
    # Role-based filtering
    if request.user.role == 'donor':
        donations = donations.filter(donor=request.user)
    elif request.user.role == 'ngo':
        donations = donations.filter(
            Q(status='Pending') | Q(assigned_ngo=request.user)
        )
    elif request.user.role == 'volunteer':
        donations = donations.filter(assigned_volunteer=request.user)
    
    return render(request, 'donations/donation_list.html', {'donations': donations})

@login_required
def donation_history(request):
    """View donation history based on user role"""
    if request.user.role == 'donor':
        donations = Donation.objects.filter(donor=request.user).order_by('-created_at')
        title = "My Donation History"
    elif request.user.role == 'ngo':
        donations = Donation.objects.filter(assigned_ngo=request.user).order_by('-updated_at')
        title = "Accepted Donations History"
    elif request.user.role == 'volunteer':
        donations = Donation.objects.filter(assigned_volunteer=request.user).order_by('-updated_at')
        title = "My Completed Tasks"
    elif request.user.role == 'admin':
        donations = Donation.objects.all().order_by('-created_at')
        title = "All Donations History"
    else:
        donations = Donation.objects.none()
        title = "Donation History"
    
    return render(request, 'donations/donation_history.html', {
        'donations': donations,
        'title': title
    })
