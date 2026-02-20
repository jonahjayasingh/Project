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
        # Simple processing for now, ideally use Django Forms
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category_id = request.POST.get('category')
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
            
            # Update account balance (naive implementation)
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
    
    # Filters
    account_id = request.GET.get('account')
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if account_id:
        transactions = transactions.filter(account_id=account_id)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if search_query:
        transactions = transactions.filter(description__icontains=search_query)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
        
    context = {
        'transactions': transactions,
        'accounts': Account.objects.all(),
        'categories': Category.objects.all(),
        'selected_account': int(account_id) if account_id else 0,
        'selected_category': int(category_id) if category_id else 0,
        'search_query': search_query or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
def reports(request):
    import json
    from django.db.models.functions import TruncMonth
    from django.db.models import Count
    
    # Filter by Account
    account_id = request.GET.get('account')
    transactions = Transaction.objects.all()
    if account_id:
        transactions = transactions.filter(account_id=account_id)

    # 1. Income vs Expense
    income_total = transactions.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = transactions.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # 2. Expenses by Category
    expense_by_category = transactions.filter(type='EXPENSE').values('category__name').annotate(total=Sum('amount')).order_by('-total')
    expense_cat_labels = [item['category__name'] or 'Uncategorized' for item in expense_by_category]
    expense_cat_data = [float(item['total']) for item in expense_by_category]

    # 3. Income by Category
    income_by_category = transactions.filter(type='INCOME').values('category__name').annotate(total=Sum('amount')).order_by('-total')
    income_cat_labels = [item['category__name'] or 'Uncategorized' for item in income_by_category]
    income_cat_data = [float(item['total']) for item in income_by_category]

    # 4. Monthly Trend (Last 6 Months) - Naive approach
    # Ideally use a robust date range, but here we just truncate to month
    monthly_trend = transactions.annotate(month=TruncMonth('date')).values('month').annotate(
        income=Sum('amount', filter=models.Q(type='INCOME')),
        expense=Sum('amount', filter=models.Q(type='EXPENSE'))
    ).order_by('month')
    
    # Taking last 6 months
    monthly_trend = monthly_trend[max(0, len(monthly_trend)-6):]
    
    trend_labels = [item['month'].strftime('%b %Y') for item in monthly_trend]
    trend_income = [float(item['income'] or 0) for item in monthly_trend]
    trend_expense = [float(item['expense'] or 0) for item in monthly_trend]

    net_savings = float(income_total) - float(expense_total)

    context = {
        'accounts': Account.objects.all(),
        'selected_account': int(account_id) if account_id else 0,
        'income_total': float(income_total),
        'expense_total': float(expense_total),
        'net_savings': net_savings,
        'expense_cat_labels': json.dumps(expense_cat_labels),
        'expense_cat_data': json.dumps(expense_cat_data),
        'income_cat_labels': json.dumps(income_cat_labels),
        'income_cat_data': json.dumps(income_cat_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_income': json.dumps(trend_income),
        'trend_expense': json.dumps(trend_expense),
    }
    return render(request, 'transactions/reports.html', context)

@login_required
def export_transactions(request):
    account_id = request.GET.get('account') 
    print(account_id)
    if account_id == 0:
        transactions = Transaction.objects.all().order_by('-date')
    else:
        transactions = Transaction.objects.filter(account_id=account_id).order_by('-date')
    print(transactions)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Amount', 'Type', 'Category', 'Account'])

    
    
    if account_id:
        transactions = transactions.filter(account_id=account_id)
        
    for txn in transactions:
        writer.writerow([txn.date, txn.description, txn.amount, txn.type, txn.category, txn.account])

    return response

@login_required
def add_category(request):
    from .forms import CategoryForm
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('add_transaction')
    else:
        form = CategoryForm()
    return render(request, 'transactions/add_category.html', {'form': form})

@login_required
def add_account(request):
    from .forms import AccountForm
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.current_balance = account.initial_balance
            account.save()
            messages.success(request, 'Account added successfully.')
            return redirect('add_transaction')
    else:
        form = AccountForm()
    return render(request, 'transactions/add_account.html', {'form': form})


@login_required
def manage_data(request):
    categories = Category.objects.all()
    accounts = Account.objects.all()
    return render(request, 'transactions/manage_data.html', {'categories': categories, 'accounts': accounts})

@login_required
def edit_category(request, pk):
    from .forms import CategoryForm
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('manage_data')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'transactions/edit_category.html', {'form': form})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
    return redirect('manage_data')

@login_required
def edit_account(request, pk):
    from .forms import AccountForm
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            
            # Recalculate current balance based on new initial balance and all transactions
            # This ensures consistency if initial balance is changed
            from django.db.models import Sum
            
            income = account.transaction_set.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
            expenses = account.transaction_set.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
            
            account.current_balance = account.initial_balance + income - expenses
            account.save()
            
            messages.success(request, 'Account updated successfully.')
            return redirect('manage_data')
    else:
        form = AccountForm(instance=account)
    return render(request, 'transactions/edit_account.html', {'form': form})

@login_required
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted successfully.')
    return redirect('manage_data')

@login_required
def edit_transaction(request, pk):
    from .forms import TransactionForm
    from decimal import Decimal
    transaction = get_object_or_404(Transaction, pk=pk)
    old_amount = transaction.amount
    old_type = transaction.type
    old_account = transaction.account

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            # Reverse old transaction impact
            if old_type == 'INCOME':
                old_account.current_balance -= old_amount
            else:
                old_account.current_balance += old_amount
            old_account.save()

            transaction = form.save()
            
            # Apply new transaction impact
            new_account = transaction.account
            if transaction.type == 'INCOME':
                new_account.current_balance += transaction.amount
            else:
                new_account.current_balance -= transaction.amount
            new_account.save()

            messages.success(request, 'Transaction updated successfully.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'transactions/edit_transaction.html', {'form': form, 'transaction': transaction})

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    account = transaction.account
    amount = transaction.amount
    type = transaction.type

    if request.method == 'POST':
        # Reverse transaction impact before delete
        from decimal import Decimal
        if type == 'INCOME':
            account.current_balance -= amount
        else:
            account.current_balance += amount
        account.save()
        
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('transaction_list')
    return render(request, 'transactions/delete_confirm.html', {'transaction': transaction})
