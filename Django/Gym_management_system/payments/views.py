from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import Payment
from .forms import PaymentForm


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_admin() or user.is_staff_member())


@login_required
@user_passes_test(is_admin_or_staff)
def payment_list(request):
    """List all payments with filters"""
    payments = Payment.objects.select_related('member__user', 'received_by').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        payments = payments.filter(
            Q(invoice_number__icontains=search_query) |
            Q(member__user__first_name__icontains=search_query) |
            Q(member__user__last_name__icontains=search_query)
        )
    
    # Filter by payment type
    type_filter = request.GET.get('type', '')
    if type_filter:
        payments = payments.filter(payment_type=type_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Calculate total
    total_amount = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'type_choices': Payment.TYPE_CHOICES,
        'status_choices': Payment.STATUS_CHOICES,
        'total_amount': total_amount,
    }
    return render(request, 'payments/payment_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def payment_detail(request, pk):
    """View payment details"""
    payment = get_object_or_404(Payment.objects.select_related('member__user', 'received_by'), pk=pk)
    
    context = {'payment': payment}
    return render(request, 'payments/payment_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def payment_create(request):
    """Record a new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.save()
            
            messages.success(request, f'Payment {payment.invoice_number} recorded successfully!')
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'title': 'Record Payment',
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def payment_edit(request, pk):
    """Edit payment (only for pending payments)"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if payment.status != 'pending':
        messages.error(request, 'Only pending payments can be edited!')
        return redirect('payments:payment_detail', pk=payment.pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Payment {payment.invoice_number} updated successfully!')
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'title': 'Edit Payment',
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def payment_refund(request, pk):
    """Process refund"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        payment.status = 'refunded'
        payment.save()
        messages.success(request, f'Payment {payment.invoice_number} refunded successfully!')
        return redirect('payments:payment_detail', pk=payment.pk)
    
    context = {'payment': payment}
    return render(request, 'payments/payment_confirm_refund.html', context)
