from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MenuItem, MenuCategory
from .forms import MenuItemForm, MenuCategoryForm
from accounts.decorators import admin_required

def menu_list_view(request):
    """Client facing menu list"""
    categories = MenuCategory.objects.all()
    cart_item_ids = []
    current_event = None
    event_id = request.GET.get('event_id')
    
    if request.user.is_authenticated:
        from cart.models import Cart
        from events.models import Event, EventSelection
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item_ids = list(cart.items.filter(food_item__isnull=False).values_list('food_item_id', flat=True))
        
        if event_id:
            current_event = get_object_or_404(Event, id=event_id, client=request.user)
            # Also include items already booked for this event
            booked_ids = list(EventSelection.objects.filter(event=current_event, food_item__isnull=False).values_list('food_item_id', flat=True))
            cart_item_ids.extend(booked_ids)
            cart_item_ids = list(set(cart_item_ids)) # Remove potential duplicates
        
    return render(request, 'food/menu_list.html', {
        'categories': categories,
        'cart_item_ids': cart_item_ids,
        'current_event': current_event
    })

@admin_required
def admin_menus_view(request):
    """Admin dashboard for menus"""
    menu_items = MenuItem.objects.all()
    categories = MenuCategory.objects.all()
    return render(request, 'food/admin_menus.html', {
        'menu_items': menu_items,
        'categories': categories
    })

@admin_required
def menu_item_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('food:admin_menus')
    else:
        form = MenuItemForm()
    return render(request, 'food/menu_item_form.html', {'form': form, 'title': 'Add Menu Item'})

@admin_required
def menu_item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated!')
            return redirect('food:admin_menus')
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'food/menu_item_form.html', {'form': form, 'title': 'Edit Menu Item'})

@admin_required
def menu_item_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted.')
        return redirect('food:admin_menus')
    return render(request, 'confirm_delete.html', {'object': item})
