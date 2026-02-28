from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Service, ServicePortfolio
from .forms import ServiceForm
from accounts.decorators import admin_required

def service_list_view(request):
    """Client facing services list"""
    services = Service.objects.all()
    cart_item_ids = []
    current_event = None
    event_id = request.GET.get('event_id')
    
    if request.user.is_authenticated:
        from cart.models import Cart
        from events.models import Event, EventSelection
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item_ids = list(cart.items.filter(service_item__isnull=False).values_list('service_item_id', flat=True))
        
        if event_id:
            current_event = get_object_or_404(Event, id=event_id, client=request.user)
            # Combine items in cart with items already booked for this event
            booked_ids = list(EventSelection.objects.filter(event=current_event, service_item__isnull=False).values_list('service_item_id', flat=True))
            cart_item_ids.extend(booked_ids)
            cart_item_ids = list(set(cart_item_ids))
            
    return render(request, 'services/service_list.html', {
        'services': services,
        'cart_item_ids': cart_item_ids,
        'current_event': current_event
    })

@admin_required
def admin_services_view(request):
    """Admin dashboard for services"""
    services = Service.objects.all()
    return render(request, 'services/admin_services.html', {'services': services})

@admin_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added successfully!')
            return redirect('services:admin_services')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Add Service'})

@admin_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated!')
            return redirect('services:admin_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Edit Service'})

@admin_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service removed.')
        return redirect('services:admin_services')
    return render(request, 'confirm_delete.html', {'object': service})

@admin_required
def service_portfolio_manage(request, pk):
    service = get_object_or_404(Service, pk=pk)
    portfolios = service.portfolio.all()
    
    if request.method == 'POST':
        from .forms import ServicePortfolioForm
        images = request.FILES.getlist('image')
        caption = request.POST.get('caption', '')
        
        if images:
            for image in images:
                ServicePortfolio.objects.create(
                    service=service,
                    image=image,
                    caption=caption
                )
            messages.success(request, f'{len(images)} images added to portfolio!')
            return redirect('services:service_portfolio_manage', pk=service.pk)
        else:
            messages.error(request, 'Please select at least one image.')
    else:
        from .forms import ServicePortfolioForm
        form = ServicePortfolioForm()
        
    return render(request, 'services/service_portfolio_manage.html', {
        'service': service,
        'portfolios': portfolios,
        'form': form
    })

@admin_required
def service_portfolio_delete(request, pk):
    portfolio = get_object_or_404(ServicePortfolio, pk=pk)
    service_pk = portfolio.service.pk
    portfolio.delete()
    messages.success(request, 'Portfolio image removed.')
    return redirect('services:service_portfolio_manage', pk=service_pk)
