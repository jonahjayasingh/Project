from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Resort, Room, Booking, BookingRoom, ResortReview, ResortReport
from .forms import UserRegistrationForm, ResortForm, ResortRegistrationForm, RoomForm, BookingForm, ReviewForm
from django.db import transaction
from django.db.models import Q, Sum, Count
from datetime import datetime, date

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_owner(user):
    return user.is_authenticated and user.role == 'owner'

def get_available_rooms(resort, check_in, check_out):
    available_rooms_data = []
    rooms = resort.rooms.all()
    
    for room in rooms:
        # Get total rooms of this type
        total = room.total_rooms
        
        # Calculate booked rooms of this type for the selected dates
        # Overlapping bookings: (start1 < end2) AND (end1 > start2)
        booked = BookingRoom.objects.filter(
            room=room,
            booking__status__in=['Confirmed', 'Checked-In'],
            booking__check_in__lt=check_out,
            booking__check_out__gt=check_in
        ).aggregate(total_booked=Sum('quantity'))['total_booked'] or 0
        
        available = total - booked
        available_rooms_data.append({
            'room': room,
            'available': max(0, available),
            'booked': booked
        })
    return available_rooms_data

def home(request):
    return render(request, 'resorts/home.html')

# --- Authentication Views ---
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registration successful. Welcome, {user.username}!")
            return redirect('resort_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'resorts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'owner':
                    return redirect('owner_dashboard')
                return redirect('resort_list')
    else:
        form = AuthenticationForm()
    return render(request, 'resorts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# --- Customer Views ---
def resort_list(request):
    category = request.GET.get('category')
    search_query = request.GET.get('search')
    location = request.GET.get('location')
    
    resorts = Resort.objects.filter(is_approved=True, is_active=True)
    
    # Get all unique locations for the filter
    locations = Resort.objects.filter(is_approved=True, is_active=True).values_list('location', flat=True).distinct().order_by('location')
    
    if category and category != 'All':
        resorts = resorts.filter(category=category)
    
    if search_query:
        resorts = resorts.filter(name__icontains=search_query)
        
    if location and location != 'All':
        resorts = resorts.filter(location=location)
        
    return render(request, 'resorts/resort_list.html', {
        'resorts': resorts,
        'selected_category': category or 'All',
        'search_query': search_query or '',
        'selected_location': location or 'All',
        'locations': locations
    })

def resort_detail(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id, is_approved=True)
    rooms = resort.rooms.all()
    reviews = resort.reviews.all().order_by('-created_at')
    return render(request, 'resorts/resort_detail.html', {
        'resort': resort,
        'rooms': rooms,
        'reviews': reviews
    })

@login_required
def report_resort(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            ResortReport.objects.create(
                resort=resort,
                user=request.user,
                reason=reason
            )
            messages.success(request, f"Thank you. Your report for {resort.name} has been submitted for review.")
        return redirect('resort_list')
    return render(request, 'resorts/report_resort.html', {'resort': resort})

def room_list(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    rooms = resort.rooms.all()
    return render(request, 'resorts/room_list.html', {'resort': resort, 'rooms': rooms})

@login_required
def book_resort(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    available_rooms = None
    check_in = None
    check_out = None
    guests_count = 1

    if request.method == 'POST' and 'check_availability' in request.POST:
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            guests_count = form.cleaned_data['guests_count']
            
            if check_in >= check_out:
                messages.error(request, "Check-out date must be after check-in date.")
            elif check_in < date.today():
                messages.error(request, "Check-in date cannot be in the past.")
            else:
                available_rooms = get_available_rooms(resort, check_in, check_out)
    
    elif request.method == 'POST' and 'confirm_booking' in request.POST:
        check_in = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%d').date()
        check_out = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%d').date()
        guests_count = int(request.POST.get('guests_count', 1))
        
        room_data = []
        total_rooms_selected = 0
        total_capacity_selected = 0
        
        for key, value in request.POST.items():
            if key.startswith('room_qty_'):
                room_id = key.split('_')[-1]
                qty = int(value)
                if qty > 0:
                    room = get_object_or_404(Room, id=room_id)
                    total_rooms_selected += qty
                    total_capacity_selected += room.capacity * qty
                    room_data.append({'room': room, 'qty': qty})

        # Policy Validation: Max rooms = Guests + 1
        if total_rooms_selected > guests_count + 1:
            messages.error(request, f"Policy Violation: You cannot book more than {guests_count + 1} rooms for a party of {guests_count}.")
            return redirect('book_resort', resort_id=resort_id)

        # Capacity Validation: Must fit all guests
        if total_capacity_selected < guests_count:
            messages.error(request, f"Insufficient Capacity: Selected rooms only fit {total_capacity_selected} guests, but you have {guests_count} guests.")
            return redirect('book_resort', resort_id=resort_id)

        booking = Booking.objects.create(
            user=request.user,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests_count,
            status='Pending'
        )
        
        stay_days = (check_out - check_in).days
        total_price = 0
        has_rooms = False
        
        for item in room_data:
            room = item['room']
            qty = item['qty']
            
            # Re-verify availability
            availability = get_available_rooms(resort, check_in, check_out)
            room_availability = next((it for it in availability if it['room'].id == room.id), None)
            
            if room_availability and room_availability['available'] >= qty:
                BookingRoom.objects.create(
                    booking=booking,
                    room=room,
                    quantity=qty
                )
                total_price += room.price * qty * stay_days
                has_rooms = True
            else:
                messages.error(request, f"Sorry, not enough {room.room_type} rooms available.")
                booking.delete()
                return redirect('book_resort', resort_id=resort_id)
        
        if has_rooms:
            booking.total_price = total_price
            booking.save()
            
            # --- Razorpay Integration with Fail-safe ---
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                data = { "amount": int(total_price * 100), "currency": "INR", "receipt": f"booking_{booking.id}" }
                payment = client.order.create(data=data)
                
                booking.razorpay_order_id = payment['id']
                booking.save()
                
                return render(request, 'resorts/payment.html', {
                    'payment': payment,
                    'booking': booking,
                    'api_key': settings.RAZORPAY_KEY_ID
                })
            except Exception as e:
                # Fail-safe: If Razorpay auth fails (dummy keys), simulate a successful order initialization
                print(f"Razorpay Error: {e}")
                mock_payment = {
                    'id': f'order_mock_{booking.id}',
                    'amount': int(total_price * 100),
                    'currency': 'INR'
                }
                booking.razorpay_order_id = mock_payment['id']
                booking.save()
                
                messages.warning(request, "System running in payment-simulation mode. Valid Razorpay keys required for live transactions.")
                return render(request, 'resorts/payment.html', {
                    'payment': mock_payment,
                    'booking': booking,
                    'api_key': settings.RAZORPAY_KEY_ID,
                    'is_mock': True
                })
            
        else:
            booking.delete()
            messages.error(request, "Please select at least one room.")
            return redirect('book_resort', resort_id=resort_id)
    
    else:
        form = BookingForm()

    return render(request, 'resorts/booking_form.html', {
        'form': form, 
        'resort': resort, 
        'available_rooms': available_rooms,
        'check_in': check_in,
        'check_out': check_out,
        'guests_count': guests_count
    })

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            payment_data = request.POST
            order_id = payment_data.get('razorpay_order_id')
            payment_id = payment_data.get('razorpay_payment_id')
            signature = payment_data.get('razorpay_signature')

            # --- Signature Verification with Mock Bypass ---
            if not (order_id.startswith('order_mock_') or payment_id.startswith('pay_mock_')):
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                params_dict = {
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                }
                client.utility.verify_payment_signature(params_dict)
            
            # Process the payment success
            booking = Booking.objects.get(razorpay_order_id=order_id)
            booking.is_paid = True
            booking.razorpay_payment_id = payment_id
            booking.status = 'Confirmed'
            booking.generate_otp()
            booking.save()
            
            messages.success(request, f"Payment successful! Booking confirmed. OTP: {booking.decrypted_otp}")
            return redirect('my_bookings')
            
        except Exception as e:
            messages.error(request, "Payment Verification Failed")
            return redirect('resort_list')
    return redirect('resort_list')

@login_required
def add_review(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    
    # Policy: Check if user has a completed/checked-in booking for this resort
    has_stayed = Booking.objects.filter(
        user=request.user, 
        booked_rooms__room__resort=resort,
        status__in=['Completed', 'Checked-In']
    ).exists()

    if not has_stayed:
        messages.error(request, "You can only review resorts where you have stayed.")
        return redirect('resort_list')

    # Prevent multiple reviews from the same user for the same resort
    if ResortReview.objects.filter(resort=resort, user=request.user).exists():
        messages.info(request, "You have already shared your testimonial for this sanctuary.")
        return redirect('resort_list')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.resort = resort
            review.user = request.user
            review.save()
            messages.success(request, f"Your testimonial for {resort.name} has been immortalized.")
            return redirect('resort_list')
    else:
        form = ReviewForm()
    
    return render(request, 'resorts/add_review.html', {'form': form, 'resort': resort})

@login_required
def my_bookings(request):
    today = date.today()
    bookings = Booking.objects.filter(
        user=request.user, 
        status__in=['Pending', 'Confirmed', 'Checked-In'],
        check_out__gte=today
    ).order_by('check_in')
    return render(request, 'resorts/my_bookings.html', {'bookings': bookings})

@login_required
def complete_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.is_paid:
        messages.info(request, "This booking is already paid.")
        return redirect('my_bookings')

    if booking.status == 'Cancelled':
        messages.error(request, "This booking has been cancelled.")
        return redirect('my_bookings')

    # Re-initialize Razorpay order or use existing one if still valid (simplified: re-init)
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        data = { "amount": int(booking.total_price * 100), "currency": "INR", "receipt": f"booking_{booking.id}" }
        payment = client.order.create(data=data)
        
        booking.razorpay_order_id = payment['id']
        booking.save()
        
        return render(request, 'resorts/payment.html', {
            'payment': payment,
            'booking': booking,
            'api_key': settings.RAZORPAY_KEY_ID
        })
    except Exception as e:
        print(f"Razorpay Error in complete_payment: {e}")
        mock_payment = {
            'id': f'order_mock_{booking.id}',
            'amount': int(booking.total_price * 100),
            'currency': 'INR'
        }
        booking.razorpay_order_id = mock_payment['id']
        booking.save()
        
        return render(request, 'resorts/payment.html', {
            'payment': mock_payment,
            'booking': booking,
            'api_key': settings.RAZORPAY_KEY_ID,
            'is_mock': True
        })

@login_required
def booking_history(request):
    today = date.today()
    bookings = Booking.objects.filter(
        user=request.user
    ).filter(
        Q(status__in=['Cancelled', 'Completed']) | Q(check_out__lt=today)
    ).order_by('-check_in')
    return render(request, 'resorts/booking_history.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    if is_admin(request.user):
        booking = get_object_or_404(Booking, id=booking_id)
    elif is_owner(request.user):
        booking = get_object_or_404(Booking, id=booking_id, booked_rooms__room__resort__owner=request.user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "Only pending bookings can be cancelled.")
    
    if is_admin(request.user):
        return redirect('admin_dashboard')
    elif is_owner(request.user):
        return redirect('admin_booking_list')
    return redirect('my_bookings')

# --- Admin Views ---
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Super Admin Dashboard: Platform-wide intelligence and monitoring.
    """
    resorts = Resort.objects.all()
    pending_resorts = resorts.filter(is_approved=False)
    
    # Global Revenue across ALL resorts
    total_revenue = Booking.objects.filter(
        status__in=['Confirmed', 'Checked-In', 'Completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # System-wide stats
    stats = {
        'total_bookings': Booking.objects.count(),
        'active_resorts': resorts.filter(is_approved=True).count(),
        'pending_approvals': pending_resorts.count(),
        'total_revenue': total_revenue,
        'user_count': User.objects.count(),
        'checkins_today': Booking.objects.filter(check_in=date.today(), status='Confirmed').count()
    }
    
    # Global recent activity
    recent_bookings = Booking.objects.all().order_by('-booking_date')[:10]
    
    return render(request, 'resorts/admin_dashboard.html', {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'pending_resorts': pending_resorts,
    })

@user_passes_test(is_admin)
def admin_resort_monitor(request):
    search_query = request.GET.get('search', '')
    resorts = Resort.objects.all().order_by('-id')
    
    if search_query:
        resorts = resorts.filter(
            Q(name__icontains=search_query) | 
            Q(location__icontains=search_query) |
            Q(owner__username__icontains=search_query)
        )
            
    pending_resorts = Resort.objects.filter(is_approved=False).order_by('-id')
    
    # Calculate stats per resort
    resort_stats = []
    for resort in resorts:
        booking_count = Booking.objects.filter(booked_rooms__room__resort=resort).distinct().count()
        revenue = Booking.objects.filter(
            booked_rooms__room__resort=resort, 
            status__in=['Confirmed', 'Checked-In', 'Completed']
        ).distinct().aggregate(total=Sum('total_price'))['total'] or 0
        
        resort_stats.append({
            'resort': resort,
            'booking_count': booking_count,
            'revenue': revenue,
            'report_count': resort.report_count
        })
    
    return render(request, 'resorts/admin_resort_monitor.html', {
        'resort_stats': resort_stats,
        'pending_resorts': pending_resorts,
        'total_resorts': resorts.count(),
        'search_query': search_query
    })

@user_passes_test(is_owner)
def owner_dashboard(request):
    """
    Owner Hub: A high-level overview of all owned properties.
    """
    resorts = Resort.objects.filter(owner=request.user)
    pending_resorts = resorts.filter(is_approved=False)
    
    # Financial summary across all properties
    total_revenue = Booking.objects.filter(
        booked_rooms__room__resort__owner=request.user,
        status__in=['Confirmed', 'Checked-In', 'Completed']
    ).distinct().aggregate(total=Sum('total_price'))['total'] or 0
    
    total_bookings = Booking.objects.filter(
        booked_rooms__room__resort__owner=request.user
    ).distinct().count()

    return render(request, 'resorts/owner_dashboard.html', {
        'resorts': resorts,
        'pending_resorts': pending_resorts,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
    })

@user_passes_test(is_owner)
def resort_dashboard(request, resort_id):
    """
    Resort-Specific Dashboard: Detailed management for ONE specific resort.
    """
    resort = get_object_or_404(Resort, id=resort_id, owner=request.user)
    
    # Stats for THIS resort only
    rooms = resort.rooms.all()
    bookings = Booking.objects.filter(booked_rooms__room__resort=resort).distinct().order_by('-booking_date')
    
    total_revenue = bookings.filter(
        status__in=['Confirmed', 'Checked-In', 'Completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    checkins_today = bookings.filter(
        check_in=date.today(),
        status='Confirmed'
    ).count()

    return render(request, 'resorts/resort_dashboard.html', {
        'resort': resort,
        'rooms': rooms,
        'bookings': bookings[:10],  # Recent 10
        'total_revenue': total_revenue,
        'checkins_today': checkins_today,
        'total_bookings': bookings.count(),
    })

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def admin_booking_list(request):
    """
    Owner Booking Console: Manage reservations for the owner's properties.
    """
    status_filter = request.GET.get('status')
    resort_filter = request.GET.get('resort')
    # Limit to current owner's resorts, or all if admin
    if is_admin(request.user):
        bookings = Booking.objects.all().distinct().order_by('-booking_date')
    else:
        bookings = Booking.objects.filter(booked_rooms__room__resort__owner=request.user).distinct().order_by('-booking_date')
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    if resort_filter:
        bookings = bookings.filter(booked_rooms__room__resort_id=resort_filter)
    
    pending_bookings = bookings.filter(status='Pending').count()
    
    return render(request, 'resorts/admin_booking_list.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'resort_filter': resort_filter,
        'pending_bookings': pending_bookings
    })

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def change_booking_status(request, booking_id, status):
    """
    Owner Action: Change booking state for an owned property.
    """
    # Security check: ensures owner owns the resort associated with the booking, or it's an admin
    if is_admin(request.user):
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, booked_rooms__room__resort__owner=request.user)
    old_status = booking.status
    
    if status in dict(Booking.STATUS_CHOICES):
        booking.status = status
        
        if status == 'Confirmed' and old_status == 'Pending':
            if booking.is_paid:
                booking.generate_otp()
                messages.success(request, f"Booking {booking.id} confirmed and OTP generated.")
            else:
                messages.info(request, f"Booking {booking.id} confirmed. OTP will be generated upon payment.")
        elif status == 'Checked-In':
            messages.success(request, f"Booking {booking.id} marked as Checked-In.")
        elif status == 'Completed':
            messages.success(request, f"Booking {booking.id} marked as Completed.")
        elif status == 'Cancelled':
            messages.success(request, f"Booking {booking.id} cancelled.")
            
        booking.save()
    
    if is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('admin_booking_list')

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def check_in_verification(request):
    """
    Owner Portal: Secure OTP verification at resort check-in.
    """
    booking = None
    if request.method == 'POST':
        otp = request.POST.get('otp')
        booking_id = request.POST.get('booking_id')
        
        # Verify ownership of the booking's resort or admin access
        if is_admin(request.user):
            booking_obj = get_object_or_404(Booking, id=booking_id, status='Confirmed')
        else:
            booking_obj = get_object_or_404(Booking, id=booking_id, status='Confirmed', booked_rooms__room__resort__owner=request.user)
        
        if booking_obj.decrypted_otp == otp:
            booking_obj.status = 'Checked-In'
            booking_obj.save()
            booking = booking_obj # Pass updated booking back to show details
            messages.success(request, f"Check-in successful for Booking {booking_obj.id}!")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'resorts/check_in_verification.html', {'booking': booking})

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def reports_page(request):
    """
    Performance Reporting: Granular behavioral and financial analytics.
    """
    if is_admin(request.user):
        base_bookings = Booking.objects.all()
        resorts_query = Resort.objects.all()
    else:
        base_bookings = Booking.objects.filter(booked_rooms__room__resort__owner=request.user).distinct()
        resorts_query = Resort.objects.filter(owner=request.user)
    
    total_bookings = base_bookings.count()
    bookings_by_status = base_bookings.values('status').annotate(count=Count('id'))
    
    # Most booked resort in the respective scope
    most_booked_resort = resorts_query.annotate(
        booking_count=Count('rooms__bookingroom__booking', distinct=True)
    ).order_by('-booking_count').first()
    
    # Occupancy stats
    active_bookings = base_bookings.filter(status__in=['Confirmed', 'Checked-In']).count()
    
    # Booking trends (last 7 days)
    import datetime
    last_7_days = date.today() - datetime.timedelta(days=7)
    trends = base_bookings.filter(booking_date__gte=last_7_days).extra(
        select={'day': "date(booking_date)"}
    ).values('day').annotate(count=Count('id')).order_by('day')

    return render(request, 'resorts/reports.html', {
        'total_bookings': total_bookings,
        'bookings_by_status': bookings_by_status,
        'most_booked_resort': most_booked_resort,
        'active_bookings': active_bookings,
        'trends': trends
    })

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def resort_create(request):
    if request.method == 'POST':
        form = ResortForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resort = form.save(commit=False)
            if request.user.role == 'owner':
                resort.owner = request.user
                resort.is_approved = False # Require approval for owners
                messages.success(request, "Resort added successfully and pending approval.")
            else:
                resort.is_approved = True # Auto-approve for admins
                
            resort.save()
            return redirect('owner_dashboard' if request.user.role == 'owner' else 'admin_dashboard')
    else:
        form = ResortForm(user=request.user)
    return render(request, 'resorts/resort_form.html', {'form': form, 'title': 'Add Resort'})

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def resort_update(request, pk):
    resort = get_object_or_404(Resort, pk=pk)
    
    # Security check: Ensure owners can only edit their own resorts
    if request.user.role == 'owner' and resort.owner != request.user:
        messages.error(request, "You are not authorized to edit this resort.")
        return redirect('owner_dashboard')

    if request.method == 'POST':
        form = ResortForm(request.POST, request.FILES, instance=resort, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Architectural record for {resort.name} updated successfully.")
            return redirect('admin_resort_monitor' if request.user.role == 'admin' else 'owner_dashboard')
    else:
        form = ResortForm(instance=resort, user=request.user)
    return render(request, 'resorts/resort_form.html', {'form': form, 'title': 'Edit Resort'})

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def resort_delete(request, pk):
    resort = get_object_or_404(Resort, pk=pk)
    
    # Security check
    if request.user.role == 'owner' and resort.owner != request.user:
        messages.error(request, "You are not authorized to delete this resort.")
        return redirect('owner_dashboard')

    if request.method == 'POST':
        resort.delete()
        messages.success(request, f"Property '{resort.name}' has been successfully decommissioned.")
        return redirect('owner_dashboard' if request.user.role == 'owner' else 'admin_dashboard')
    return render(request, 'resorts/resort_confirm_delete.html', {'object': resort})

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def room_create(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    
    if request.user.role == 'owner' and resort.owner != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect('owner_dashboard')

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES) # Added request.FILES support just in case
        if form.is_valid():
            room = form.save(commit=False)
            room.resort = resort
            room.save()
            return redirect('owner_dashboard' if request.user.role == 'owner' else 'admin_dashboard')
    else:
        form = RoomForm(initial={'resort': resort})
    return render(request, 'resorts/room_form.html', {'form': form, 'title': 'Add Room', 'resort': resort})

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    
    # Security check: Admins can edit anything, Owners can only edit their own
    if request.user.role == 'owner' and room.resort.owner != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect('owner_dashboard')

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f"{room.room_type} configuration updated successfully.")
            return redirect('admin_dashboard' if request.user.role == 'admin' else 'owner_dashboard')
    else:
        form = RoomForm(instance=room)
    return render(request, 'resorts/room_form.html', {'form': form, 'title': 'Edit Room', 'resort': room.resort})

@user_passes_test(lambda u: is_admin(u) or is_owner(u))
def register_resort(request):
    if request.method == 'POST':
        form = ResortRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            resort = form.save(commit=False)
            resort.owner = request.user
            resort.is_approved = False
            resort.save()
            messages.success(request, "Resort registered successfully. Waiting for admin approval.")
            return redirect('resort_list')
    else:
        form = ResortRegistrationForm()
    return render(request, 'resorts/register_resort.html', {'form': form})

@user_passes_test(is_admin)
def approve_resort(request, pk):
    resort = get_object_or_404(Resort, pk=pk)
    resort.is_approved = True
    resort.save()
    messages.success(request, f"Resort '{resort.name}' has been approved.")
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def toggle_resort_status(request, pk):
    resort = get_object_or_404(Resort, pk=pk)
    resort.is_active = not resort.is_active
    resort.save()
    status = "activated" if resort.is_active else "deactivated"
    messages.success(request, f"Resort '{resort.name}' has been {status}.")
    return redirect('admin_resort_monitor')

@user_passes_test(is_admin)
def resort_delete_admin(request, pk):
    resort = get_object_or_404(Resort, pk=pk)
    name = resort.name
    resort.delete()
    messages.success(request, f"Resort '{name}' has been permanently removed.")
    return redirect('admin_resort_monitor')

@user_passes_test(is_owner)
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    
    if room.resort.owner != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect('owner_dashboard')

    if request.method == 'POST':
        room.delete()
        return redirect('owner_dashboard')
    return render(request, 'resorts/confirm_delete.html', {'object': room})
