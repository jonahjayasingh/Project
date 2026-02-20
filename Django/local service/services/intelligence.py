import math
from django.conf import settings
from .models import ServiceProvider, Booking, FavoriteProvider, Category
from opencage.geocoder import OpenCageGeocode

def geocode_address(address):
    """
    Convert a text address to (lat, lon, formatted_address) using OpenCage Geocode API
    """
    if not address:
        return None, None, None
    
    api_key = getattr(settings, 'OPENCAGE_API_KEY', None)
    if not api_key:
        print("Geocoding Error: OPENCAGE_API_KEY not found in settings.")
        return None, None, None

    try:
        geocoder = OpenCageGeocode(api_key)
        results = geocoder.geocode(address)
        if results and len(results) > 0:
            lat = results[0]['geometry']['lat']
            lon = results[0]['geometry']['lng']
            formatted = results[0].get('formatted')
            return lat, lon, formatted
    except Exception as e:
        print(f"OpenCage Geocoding error: {e}")
    
    return None, None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')
        
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def calculate_ranking_score(provider, user_lat=None, user_lon=None, user_prefs=None):
    """
    Unified Provider Ranking Engine
    Final Score = 
    0.30 * Rating +
    0.20 * Completion Rate +
    0.15 * Punctuality Score +
    0.15 * Acceptance Rate +
    0.10 * Distance Factor +
    0.10 * Response Speed
    """
    # 1. Rating Factor (0-5 scale, normalize to 0-1)
    rating_factor = (provider.rating / 5.0) * 0.30
    
    # 2. Completion Factor (0-100 scale, normalize to 0-1)
    completion_factor = (provider.completion_rate / 100.0) * 0.20
    
    # 3. Punctuality Factor (0-100 scale, normalize to 0-1)
    punctuality_factor = (provider.on_time_rate / 100.0) * 0.15

    # 4. Acceptance Factor (Responsiveness)
    acceptance_factor = (provider.acceptance_rate / 100.0) * 0.15
    
    # 5. Distance Factor (closer is better)
    distance_factor = 0
    max_dist = user_prefs.distance_tolerance_km if user_prefs else 50
    if user_lat and user_lon and provider.latitude and provider.longitude:
        dist = haversine_distance(user_lat, user_lon, provider.latitude, provider.longitude)
        dist_score = max(0, (max_dist - dist) / max_dist)
        distance_factor = dist_score * 0.10
    else:
        distance_factor = 0.05
        
    # 6. Response Speed
    speed_score = max(0, (120 - provider.response_speed_minutes) / 120.0)
    response_factor = speed_score * 0.10
    
    total_score = rating_factor + completion_factor + punctuality_factor + acceptance_factor + distance_factor + response_factor
    
    # Preference Boosts
    final_score = total_score * 100
    if user_prefs:
        # Quality priority: Boost top-rated
        if user_prefs.quality_priority and provider.rating >= 4.5:
            final_score += 5
        # Budget priority: Boost low cost (This is a bit tricky, but let's say < 500/hr)
        if user_prefs.budget_tolerance == 'low' and provider.price_per_hour <= 500:
            final_score += 5
            
    return round(final_score, 2)

def get_recommendations(user):
    """
    Personalized Recommendation Engine
    """
    from .models import UserProfile, Booking
    profile, _ = UserProfile.objects.get_or_create(user=user)
    u_lat, u_lon = profile.latitude, profile.longitude
    
    # Base queryset
    providers = ServiceProvider.objects.filter(is_active=True)
    
    # Filter by user's distance tolerance
    if u_lat and u_lon:
        nearby_ids = []
        for p in providers:
            if p.latitude and p.longitude:
                if haversine_distance(u_lat, u_lon, p.latitude, p.longitude) <= profile.distance_tolerance_km:
                    nearby_ids.append(p.id)
        providers = providers.filter(id__in=nearby_ids)

    # Calculate scores and sort
    scored_providers = []
    for p in providers:
        score = calculate_ranking_score(p, u_lat, u_lon, profile)
        
        # Preference Boosts
        # 1. Favorite Categories
        if profile.favorite_categories.filter(id__in=p.categories.all()).exists():
            score += 10
        # 2. Category Affinity (Recent)
        if p.categories.filter(id__in=profile.recent_categories).exists():
            score += 5
        # 3. High Rating in History
        if Booking.objects.filter(user=user, provider=p, review__rating__gte=4).exists():
            score += 15
            
        scored_providers.append((p, score))
    
    # Sort by score descending
    scored_providers.sort(key=lambda x: x[1], reverse=True)
    
    return [item[0] for item in scored_providers[:6]]

def is_provider_available(provider, date, time_slot):
    """
    Check for calendar conflicts
    """
    return not Booking.objects.filter(
        provider=provider, 
        date=date, 
        time_slot=time_slot,
        status__in=['ACCEPTED', 'PENDING']
    ).exists()

def get_emergency_providers(user, category=None):
    """
    Available Now / Emergency Mode logic
    """
    from .models import UserProfile
    profile = None
    if user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=user)
    import datetime
    
    today = datetime.date.today()
    # Simplified availability: Any pro with fewer than 3 bookings today is "available now"
    # In a real app, this would check the current hour slot
    active_providers = ServiceProvider.objects.filter(is_active=True)
    if category:
        active_providers = active_providers.filter(categories=category)
        
    emergency_list = []
    for p in active_providers:
        daily_bookings = Booking.objects.filter(provider=p, date=today).count()
        if daily_bookings < 5: # Workload-aware limit
             u_lat = profile.latitude if profile else None
             u_lon = profile.longitude if profile else None
             score = calculate_ranking_score(p, u_lat, u_lon, profile)
             # Boost for proximity in emergency
             if u_lat and u_lon:
                 dist = haversine_distance(u_lat, u_lon, p.latitude, p.longitude)
                 if dist < 10: score += 20
             emergency_list.append((p, score))
             
    emergency_list.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in emergency_list[:5]]

def estimate_cost(provider, expected_hours):
    """
    Cost Estimation System
    """
    base_rate = float(provider.price_per_hour)
    total = base_rate * float(expected_hours)
    
    # Could add service fees or dynamic pricing logic here
    return {
        'hourly': base_rate,
        'estimated_total': round(total, 2),
        'currency': '₹'
    }
