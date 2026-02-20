from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import admin_required
from .models import Vendor
from .forms import VendorForm

@admin_required
def vendor_list_view(request):
    """
    List all vendors (Admin only).
    """
    vendors = Vendor.objects.all()
    return render(request, 'vendors/vendor_list.html', {'vendors': vendors})


@admin_required
def vendor_create_view(request):
    """
    Create a new vendor (Admin only).
    """
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" created successfully!')
            return redirect('vendors:vendor_list')
    else:
        form = VendorForm()
    
    return render(request, 'vendors/vendor_form.html', {'form': form, 'action': 'Create'})


@admin_required
def vendor_update_view(request, pk):
    """
    Update an existing vendor (Admin only).
    """
    vendor = get_object_or_404(Vendor, pk=pk)
    
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vendor "{vendor.name}" updated successfully!')
            return redirect('vendors:vendor_list')
    else:
        form = VendorForm(instance=vendor)
    
    return render(request, 'vendors/vendor_form.html', {
        'form': form,
        'action': 'Update',
        'vendor': vendor
    })


@admin_required
def vendor_delete_view(request, pk):
    """
    Delete a vendor (Admin only).
    """
    vendor = get_object_or_404(Vendor, pk=pk)
    
    if request.method == 'POST':
        vendor_name = vendor.name
        vendor.delete()
        messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
        return redirect('vendors:vendor_list')
    
    return render(request, 'vendors/vendor_confirm_delete.html', {'vendor': vendor})
