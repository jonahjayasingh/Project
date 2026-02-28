from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from food.models import MenuItem
from services.models import Service
from events.models import Event, EventSelection

@login_required
def cart_detail_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    # Get user's events to link the cart
    user_events = Event.objects.filter(client=request.user)
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'user_events': user_events
    })

@login_required
def update_guest_count_view(request):
    if request.method == 'POST':
        guest_count = int(request.POST.get('guest_count', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.guest_count = guest_count
        cart.save()
        messages.success(request, f"Guest count updated to {guest_count}. Pricing adjusted.")
    return redirect('cart:cart_detail')

@login_required
def add_to_cart_view(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        service_id = request.POST.get('service_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        if food_id:
            food_item = get_object_or_404(MenuItem, id=food_id)
            item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
            if not created:
                item.quantity += quantity
                item.save()
            messages.success(request, f"{food_item.name} added to cart.")
        
        if service_id:
            service_item = get_object_or_404(Service, id=service_id)
            item, created = CartItem.objects.get_or_create(cart=cart, service_item=service_item)
            if not created:
                item.quantity += quantity
                item.save()
            messages.success(request, f"{service_item.name} added to cart.")
            
        # Carry forward event_id in redirect if present
        event_id = request.POST.get('event_id')
        referer = request.META.get('HTTP_REFERER', '')
        if event_id and 'event_id' not in referer:
            # Simple way to append or replace event_id in referer for redirect
            from django.utils.http import urlencode
            sep = '&' if '?' in referer else '?'
            return redirect(f"{referer}{sep}event_id={event_id}")
            
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))

@login_required
def update_item_quantity_view(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if quantity > 0:
            item.quantity = quantity
            item.save()
            messages.success(request, f"Quantity for {item.service_item.name if item.service_item else item.food_item.name} updated.")
        else:
            item.delete()
            messages.success(request, "Item removed from cart.")
            
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart_view(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:cart_detail')

@login_required
def remove_food_view(request, food_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.filter(cart=cart, food_item_id=food_id).delete()
    messages.success(request, "Removed from your selection.")
    
    event_id = request.POST.get('event_id')
    referer = request.META.get('HTTP_REFERER', '')
    if event_id and 'event_id' not in referer:
        sep = '&' if '?' in referer else '?'
        return redirect(f"{referer}{sep}event_id={event_id}")
        
    return redirect(request.META.get('HTTP_REFERER', 'food:menu_list'))

@login_required
def remove_service_view(request, service_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.filter(cart=cart, service_item_id=service_id).delete()
    messages.success(request, "Removed from your selection.")
    
    event_id = request.POST.get('event_id')
    referer = request.META.get('HTTP_REFERER', '')
    if event_id and 'event_id' not in referer:
        sep = '&' if '?' in referer else '?'
        return redirect(f"{referer}{sep}event_id={event_id}")
        
    return redirect(request.META.get('HTTP_REFERER', 'services:service_list'))

@login_required
def finalize_booking_view(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        cart = get_object_or_404(Cart, user=request.user)
        event = get_object_or_404(Event, id=event_id, client=request.user)
        
        # Move items from cart to event selections (Incrementally)
        for item in cart.items.all():
            if item.food_item:
                unit_price = item.food_item.price
                qty = cart.guest_count
                # Check if this food item already exists for this event
                selection, created = EventSelection.objects.get_or_create(
                    event=event, 
                    food_item=item.food_item,
                    defaults={'quantity': qty, 'unit_price': unit_price, 'total_price': item.subtotal()}
                )
                if not created:
                    selection.quantity = qty
                    selection.total_price = item.subtotal()
                    selection.save()
            else:
                unit_price = item.service_item.base_price
                qty = item.quantity
                selection, created = EventSelection.objects.get_or_create(
                    event=event,
                    service_item=item.service_item,
                    defaults={'quantity': qty, 'unit_price': unit_price, 'total_price': item.subtotal()}
                )
                if not created:
                    selection.quantity += qty
                    selection.total_price = selection.total_price + item.subtotal()
                    selection.save()
        
        # Update event total cost based on ALL selections now
        event.total_cost = sum(s.total_price for s in event.selections.all())
        event.save()
        
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, f"Booking finalized for event: {event.event_type.name} on {event.date}")
        return redirect('events:event_detail', pk=event.pk)
    
    return redirect('cart:cart_detail')
