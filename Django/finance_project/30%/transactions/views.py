from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Transaction, Account, Category
from django.db import models
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout,authenticate
import csv

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    # Add Tailwind classes to form fields
    for field in form.fields.values():
        field.widget.attrs.update({
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
        
    return render(request, 'registration/register.html', {'form': form})

def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def userlogout(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    accounts = Account.objects.all()
    recent_transactions = Transaction.objects.order_by('-date')[:5]
    total_balance = sum(acc.current_balance for acc in accounts)
    
    income = Transaction.objects.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = Transaction.objects.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'total_balance': total_balance,
        'income': income,
        'expenses': expenses,
    }
    return render(request, 'transactions/dashboard.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category_id = request.GET.get('category') or request.POST.get('category')
        account_id = request.POST.get('account')
        type = request.POST.get('type')
        
        try:
            category = Category.objects.get(id=category_id) if category_id else None
            account = Account.objects.get(id=account_id)
            
            Transaction.objects.create(
                description=description,
                amount=amount,
                date=date,
                category=category,
                account=account,
                type=type
            )
            
            from decimal import Decimal
            if type == 'INCOME':
                account.current_balance += Decimal(amount)
            else:
                account.current_balance -= Decimal(amount)
            account.save()
            
            messages.success(request, 'Transaction added successfully.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error adding transaction: {e}')
            
    categories = Category.objects.all()
    accounts = Account.objects.all()
    return render(request, 'transactions/add_transaction.html', {'categories': categories, 'accounts': accounts})

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    context = {
        'transactions': transactions,
        'accounts': Account.objects.all(),
    }
    return render(request, 'transactions/transaction_list.html', context)
