from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Category, ServiceProvider, Booking, Review, ChatMessage, UserProfile, FavoriteProvider, Notification, Dispute
from .forms import UserSignupForm, ReviewForm, ServiceProviderForm
from . import intelligence, notifications
from django.db.models import Q, Avg
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch

import re
import requests
import json
import datetime

# Configure Ollama
OLLAMA_URL = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
AI_MODEL = getattr(settings, 'OLLAMA_MODEL', 'deepseek-v3.1:671b-cloud')

def call_ollama(messages):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": AI_MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get('message', {}).get('content', '').strip()
        else:
            print(f"Ollama Error Status: {response.status_code}")
    except Exception as e:
        print(f"Ollama Connection Error: {e}")
    return None

def parse_search_query_ai(query):
    categories = list(Category.objects.values_list('name', flat=True))
    prompt = f"""
    The user is looking for a service: "{query}"
    Available categories: {', '.join(categories)}
    
    Extract the following in JSON format:
    - category: (Match one of the available categories or null)
    - location: (Extract city or area if mentioned, else null)
    - time: (Extract time/date if mentioned, else null)
    - budget: (Extract numeric budget if mentioned, else null)
    
    Example: "Need a plumber in Nagercoil tomorrow" -> {{"category": "Plumbing", "location": "Nagercoil", "time": "tomorrow", "budget": null}}
    Return ONLY JSON.
    """
    
    messages = [
        {"role": "system", "content": "You are an intelligent service search parser. Return ONLY valid JSON."},
        {"role": "user", "content": prompt}
    ]
    
    content = call_ollama(messages)
    try:
        if content:
            # Clean possible markdown
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print(f"JSON Parse Error: {e}")
    return {"category": None, "location": None, "time": None, "budget": None}

def get_ranked_providers(categories=None, location=None, user_lat=None, user_lon=None, sort_by=None, user_prefs=None):
    providers = ServiceProvider.objects.filter(is_active=True, is_approved=True)
    if categories:
        providers = providers.filter(categories__in=categories).distinct()
    if location:
        providers = providers.filter(location__icontains=location)
    
    # Calculate intelligent scores
    provider_list = []
    for p in providers:
        # Distance Filter
        if user_lat and user_lon and p.latitude and p.longitude:
            dist = intelligence.haversine_distance(user_lat, user_lon, p.latitude, p.longitude)
            max_dist = user_prefs.distance_tolerance_km if user_prefs else 50
            if dist > max_dist:
                continue
        
        score = intelligence.calculate_ranking_score(p, user_lat, user_lon, user_prefs)
        p.final_score = score
        provider_list.append(p)
    
    # Sorting logic
    if sort_by == 'price_asc':
        provider_list.sort(key=lambda x: x.price_per_hour)
    elif sort_by == 'price_desc':
        provider_list.sort(key=lambda x: x.price_per_hour, reverse=True)
    elif sort_by == 'rating_desc':
        provider_list.sort(key=lambda x: x.rating, reverse=True)
    elif sort_by == 'jobs_desc':
        provider_list.sort(key=lambda x: x.jobs_completed, reverse=True)
    else:
        # Default sort by rank score
        provider_list.sort(key=lambda x: x.final_score, reverse=True)
        
    return provider_list

def generate_ai_recommendation(query, detected_cat, providers):
    if not providers:
        return None
    
    provider_info = [f"{p.name} (₹{p.price_per_hour}/hr, Rating: {p.rating}, Score: {getattr(p, 'final_score', 0):.2f}, Location: {p.location})" for p in providers[:3]]
    
    prompt = f"""
    User Query: "{query}"
    Top Professionals Found:
    {chr(10).join(provider_info)}
    
    Write a short (2-3 sentences) personalized recommendation. Explain why these professionals are a good match.
    """
    
    messages = [
        {"role": "system", "content": "You are a helpful AI service advisor."},
        {"role": "user", "content": prompt}
    ]
    
    return call_ollama(messages)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    from django.db.models import Prefetch
    approved_providers = ServiceProvider.objects.filter(is_active=True, is_approved=True)
    categories = Category.objects.prefetch_related(Prefetch('providers', queryset=approved_providers))
    user_location = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_location = profile.location_name
    # Get unique locations from active providers
    provider_locations = ServiceProvider.objects.filter(is_active=True, is_approved=True).values_list('location', flat=True).distinct()
    
    return render(request, 'services/home.html', {
        'categories': categories,
        'user_location': user_location,
        'locations': sorted(list(set(provider_locations)))
    })

def search_results(request):
    query = request.GET.get('q', '')
    category_ids = request.GET.getlist('category') # Support multiple
    
    # 1. AI Parsing
    intent = parse_search_query_ai(query)
    
    detected_cat_name = intent.get('category')
    parsed_location = intent.get('location')
    
    active_cats = Category.objects.none()
    if category_ids:
        active_cats = Category.objects.filter(pk__in=category_ids)
    elif detected_cat_name:
        active_cats = Category.objects.filter(name__iexact=detected_cat_name)
        
    # 2. Ranking & Filtering
    u_lat = None
    u_lon = None
    profile = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        u_lat = profile.latitude
        u_lon = profile.longitude
    
    search_loc = parsed_location if parsed_location else request.GET.get('location', '')
    sort_method = request.GET.get('sort', '')
    emergency_mode = request.GET.get('emergency') == 'on'
    
    if emergency_mode:
        providers = intelligence.get_emergency_providers(request.user, category=active_cats.first())
    else:
        providers = get_ranked_providers(
            categories=active_cats, 
            location=search_loc, 
            user_lat=u_lat, 
            user_lon=u_lon, 
            sort_by=sort_method,
            user_prefs=profile
        )
    
    # 3. AI Recommendation
    primary_cat = active_cats.first() if active_cats.exists() else None
    ai_recommendation = generate_ai_recommendation(query, primary_cat, providers)
    
    # Get unique locations for the filter
    provider_locations = ServiceProvider.objects.filter(is_active=True, is_approved=True).values_list('location', flat=True).distinct()
    
    context = {
        'providers': providers,
        'query': query,
        'active_cats': active_cats,
        'active_cat_ids': [str(c.id) for c in active_cats],
        'location': search_loc,
        'intent': intent,
        'ai_recommendation': ai_recommendation,
        'categories': Category.objects.prefetch_related(Prefetch('providers', queryset=ServiceProvider.objects.filter(is_active=True, is_approved=True))),
        'locations': sorted(list(set(provider_locations)))
    }
    return render(request, 'services/search_results.html', context)

def provider_detail(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    today = datetime.date.today()
    reviews = provider.reviews.all().order_by('-created_at')
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteProvider.objects.filter(user=request.user, provider=provider).exists()
    
    # Availability Preview for 14 days
    availability = []
    now = datetime.datetime.now()
    for i in range(14):
        date = today + datetime.timedelta(days=i)
        # Generate hourly slots from 8 AM to 8 PM
        slots = []
        for h in range(8, 21):
            slot_time = f"{h:02d}:00"
            # If it's today, only show future slots
            if i == 0:
                if h <= now.hour:
                    continue
            slots.append(slot_time)
            
        available_slots = [s for s in slots if intelligence.is_provider_available(provider, date, s)]
        availability.append({'date': date, 'slots': available_slots})

    context = {
        'provider': provider,
        'today': today,
        'reviews': reviews,
        'is_favorite': is_favorite,
        'availability': availability,
    }
    return render(request, 'services/provider_detail.html', context)


@login_required
def book_appointment(request, pk):
    if request.method == "POST":
        provider = get_object_or_404(ServiceProvider, pk=pk)
        date_str = request.POST.get('date')
        slot_str = request.POST.get('slot')
        hours = int(request.POST.get('hours', 2))
        
        # 1. Past Date Validation
        try:
            booking_datetime = datetime.datetime.strptime(f"{date_str} {slot_str}", "%Y-%m-%d %H:%M")
            if booking_datetime < datetime.datetime.now():
                messages.error(request, "You cannot book an appointment in the past.")
                return redirect('provider_detail', pk=pk)
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('provider_detail', pk=pk)

        # 2. Conflict Detection
        if not intelligence.is_provider_available(provider, date_str, slot_str):
            messages.error(request, "This professional is already booked for the selected time. Please choose another slot.")
            return redirect('provider_detail', pk=pk)

        booking = Booking.objects.create(
            user=request.user,
            provider=provider,
            date=date_str,
            time_slot=slot_str,
            estimated_hours=hours,
            status='PENDING'
        )
        
        # Increment Provider Metrics
        provider.total_requests += 1
        provider.save()
        
        notifications.notify_booking_status(booking)
        messages.success(request, f"Appointment requested with {provider.name}!")
        return redirect('dashboard')
    return redirect('provider_detail', pk=pk)

@login_required
def dashboard(request):
    # Dynamic Preferences Verification
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Bookings made by the user
    all_bookings = Booking.objects.filter(user=request.user).order_by('-date', '-time_slot')
    upcoming_bookings = all_bookings.filter(date__gte=datetime.date.today(), status__in=['PENDING', 'ACCEPTED'])
    past_bookings = all_bookings.filter(Q(date__lt=datetime.date.today()) | Q(status__in=['COMPLETED', 'CANCELLED']))
    
    # Bookings received as a pro
    pro_bookings = None
    if hasattr(request.user, 'provider_profile'):
        pro_bookings = Booking.objects.filter(provider=request.user.provider_profile).order_by('-date', '-time_slot')
    
    # Personalized Recommendations using the new intelligence engine
    recommendations = intelligence.get_recommendations(request.user)
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'pro_bookings': pro_bookings,
        'profile': profile,
        'recommendations': recommendations,
        'favorites': FavoriteProvider.objects.filter(user=request.user),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'disputes': Dispute.objects.filter(user=request.user),
    }
    return render(request, 'services/dashboard.html', context)

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if a review already exists for this booking
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this service.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.provider = booking.provider
            review.booking = booking
            review.save()
            
            # Update Provider Rating & Metrics
            avg_rating = Review.objects.filter(provider=booking.provider).aggregate(Avg('rating'))['rating__avg']
            booking.provider.rating = round(avg_rating, 2) if avg_rating else 0.0
            # Only increment jobs_completed if it wasn't already marked completed by the pro
            if booking.status != 'COMPLETED':
                booking.provider.jobs_completed += 1
            
            booking.status = 'COMPLETED'
            booking.provider.save()
            booking.save()
            
            messages.success(request, "Thank you for your feedback! Your review has been published.")
            return redirect('dashboard')
    else:
        form = ReviewForm()
    return render(request, 'services/submit_review.html', {'form': form, 'booking': booking})

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.location_name = request.POST.get('location_name')
        # Explicitly handle latitude and longitude
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        try:
            profile.latitude = float(lat) if lat and lat.strip() else None
            profile.longitude = float(lon) if lon and lon.strip() else None
        except ValueError:
            profile.latitude = None
            profile.longitude = None
            
        # Fallback: If no coordinates from GPS, try Geocoding the address name
        if not profile.latitude or not profile.longitude:
            g_lat, g_lon, formatted = intelligence.geocode_address(profile.location_name)
            if g_lat and g_lon:
                profile.latitude = g_lat
                profile.longitude = g_lon
                # Update location_name with the full formatted region if it was just a raw keyword
                if formatted:
                    profile.location_name = formatted
            
        profile.save()
        messages.success(request, "Intelligence Profile Updated Successfully!")
        return redirect('dashboard')
    return render(request, 'services/update_profile.html')

@login_required
def favorites_list(request):
    favorites = FavoriteProvider.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/favorites_list.html', {'favorites': favorites})

@login_required
def toggle_favorite(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    fav, created = FavoriteProvider.objects.get_or_create(user=request.user, provider=provider)
    if not created:
        fav.delete()
        messages.info(request, f"Removed {provider.name} from favorites.")
    else:
        messages.success(request, f"Added {provider.name} to favorites.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('notifications_list')

# Overriding signup to send confirmation notification
def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            Notification.objects.create(
                user=user,
                title="Welcome to ServiceFinder!",
                message="Your intelligence profile is active. Get started by setting your location.",
                notification_type='SYSTEM'
            )
            return redirect('dashboard')
    else:
        form = UserSignupForm()
    return render(request, 'services/signup.html', {'form': form})

@login_required
def ai_chatbot(request):
    if request.method == 'POST':
        user_msg = request.POST.get('message')
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # 1. Extract Intent and Constraints via Parsing logic
        intent = parse_search_query_ai(user_msg)
        
        # 2. Query Database using Ranking Engine
        active_cats = Category.objects.filter(name__iexact=intent.get('category')) if intent.get('category') else None
        u_lat, u_lon = profile.latitude, profile.longitude
        
        # Handle "cheapest" constraint
        sort_by = 'price_asc' if "cheap" in user_msg.lower() or "budget" in user_msg.lower() or "cost" in user_msg.lower() else None
        
        providers = get_ranked_providers(
            categories=active_cats, 
            location=intent.get('location'), 
            user_lat=u_lat, 
            user_lon=u_lon,
            sort_by=sort_by,
            user_prefs=profile
        )
        
        # 3. Decision-Support Formatting
        provider_brief = ""
        if providers:
            p = providers[0]
            provider_brief = f"Based on my analysis, I recommend **{p.name}**. They have a rank score of {getattr(p, 'final_score', 0)} and charge ₹{p.price_per_hour}/hr. <a href='/provider/{p.id}/' class='btn btn-sm btn-link p-0 fw-bold'>View details</a>"

        # 4. Final completion
        system_prompt = "You are a ServiceFinder assistant. Answer helpfully."
        
        prompt = f"The user asked: '{user_msg}'. Intent detected: {intent}. {provider_brief}. Provide a helpful, concise response based on this context. If no providers found, suggest general search."
        
        response_text = call_ollama([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        if not response_text:
            response_text = provider_brief if provider_brief else "Searching local experts for you..."

        ChatMessage.objects.create(user=request.user, message=user_msg, response=response_text)
        return render(request, 'services/chatbot_response.html', {'response': response_text, 'message': user_msg})
    
    history = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:15]
    if request.headers.get('HX-Request'):
        return render(request, 'services/chatbot_history_partial.html', {'history': history})
    
    return redirect('home')

@login_required
def register_provider(request):
    try:
        instance = request.user.provider_profile
    except ServiceProvider.DoesNotExist:
        instance = None

    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.user = request.user
            
            # Explicitly capture lat/lon from POST in case form validation missed it
            lat = request.POST.get('latitude')
            lon = request.POST.get('longitude')
            try:
                provider.latitude = float(lat) if lat and lat.strip() else None
                provider.longitude = float(lon) if lon and lon.strip() else None
            except ValueError:
                pass # Already handled by form or default
            
            # Fallback: Geocode if GPS skipped
            if not provider.latitude or not provider.longitude:
                g_lat, g_lon, formatted = intelligence.geocode_address(provider.location)
                if g_lat and g_lon:
                    provider.latitude = g_lat
                    provider.longitude = g_lon
                    if formatted:
                        provider.location = formatted
                
            provider.save()
            form.save_m2m() # Required when commit=False
            messages.success(request, "Professional profile updated successfully!")
            return redirect('dashboard')
    else:
        form = ServiceProviderForm(instance=instance)
    
    return render(request, 'services/register_provider.html', {'form': form, 'instance': instance})

@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Only provider assigned can change status
    if hasattr(request.user, 'provider_profile') and booking.provider == request.user.provider_profile:
        if status in ['ACCEPTED', 'CANCELLED', 'COMPLETED']:
            # Handle stats
            if status == 'ACCEPTED' and booking.status == 'PENDING':
                booking.provider.accepted_requests += 1
            elif status == 'CANCELLED' and booking.status == 'ACCEPTED':
                booking.provider.cancelled_by_provider += 1
            elif status == 'COMPLETED' and booking.status != 'COMPLETED':
                booking.provider.jobs_completed += 1
                
            booking.status = status
            booking.save()
            booking.provider.save()
            
            # Send dynamic notifications
            notifications.notify_booking_status(booking)
            messages.success(request, f"Booking status updated to {status.lower()}.")
    
    return redirect('dashboard')

@login_required
def update_user_preferences(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.budget_tolerance = request.POST.get('budget_tolerance', 'mid')
        profile.distance_tolerance_km = int(request.POST.get('distance_tolerance', 30))
        profile.quality_priority = request.POST.get('quality_priority') == 'on'
        
        category_ids = request.POST.getlist('favorite_categories')
        profile.favorite_categories.set(Category.objects.filter(id__in=category_ids))
        
        profile.save()
        messages.success(request, "Preferences updated successfully!")
        return redirect('dashboard')
    
    categories = Category.objects.all()
    context = {
        'profile': profile,
        'categories': categories,
    }
    return render(request, 'services/update_preferences.html', context)

@login_required
def report_dispute(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if hasattr(booking, 'dispute'):
        messages.info(request, "A dispute for this booking is already open.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description')
        evidence = request.FILES.get('evidence')
        
        Dispute.objects.create(
            booking=booking,
            user=request.user,
            issue_type=issue_type,
            description=description,
            evidence=evidence
        )
        messages.success(request, "Dispute reported. Our team will review it shortly.")
        return redirect('dashboard')
        
    return render(request, 'services/report_dispute.html', {'booking': booking, 'issue_types': Dispute.ISSUE_TYPES})

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff only.")
        return redirect('dashboard')
    
    q = request.GET.get('q', '')
    cat_id = request.GET.get('category')
    status = request.GET.get('status', 'all')
    
    providers = ServiceProvider.objects.all()
    
    if status == 'approved':
        providers = providers.filter(is_approved=True)
    elif status == 'pending':
        providers = providers.filter(is_approved=False)
    
    if q:
        providers = providers.filter(Q(name__icontains=q) | Q(location__icontains=q))
    
    if cat_id:
        providers = providers.filter(categories__id=cat_id)
        
    providers = providers.distinct().order_by('-id')
    
    return render(request, 'services/staff_dashboard.html', {
        'providers': providers,
        'categories': Category.objects.all(),
        'query': q,
        'active_category': cat_id,
        'active_status': status
    })

@login_required
def approve_provider(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.is_approved = True
    provider.save()
    
    # Notify the user
    if provider.user:
        Notification.objects.create(
            user=provider.user,
            title="Profile Approved!",
            message="Your professional profile has been approved! You are now visible on the platform.",
            notification_type='SYSTEM'
        )
    
    messages.success(request, f"Approved {provider.name} successfully.")
    return redirect('staff_dashboard')

@login_required
def revoke_provider(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.is_approved = False
    provider.save()
    
    # Notify the user
    if provider.user:
        Notification.objects.create(
            user=provider.user,
            title="Profile Access Revoked",
            message="Your professional profile approval has been revoked. Please contact support for more details.",
            notification_type='SYSTEM'
        )
    
    messages.warning(request, f"Revoked permission for {provider.name}.")
    return redirect('staff_dashboard')
