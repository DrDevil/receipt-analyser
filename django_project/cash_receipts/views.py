from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Receipt, ReceiptItem
from .forms import ReceiptForm, SignupForm


def index(request):
    """Homepage - show recent receipts."""
    receipts_list = Receipt.objects.all()[:10]
    return render(request, 'cash_receipts/index.html', {
        'receipts': receipts_list
    })


def user_profile(request, username):
    """Show all receipts for a specific user."""
    user = get_object_or_404(User, username=username)
    receipts = user.receipts.all()
    paginator = Paginator(receipts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'cash_receipts/user.html', {
        'profile_user': user,
        'page_obj': page_obj,
    })


@login_required
def add_receipt(request):
    """Add a new receipt with optional line items."""
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.owner = request.user
            receipt.save()

            # Handle line items
            product_name = request.POST.get('product_name')
            quantity = request.POST.get('quantity')
            unit_price = request.POST.get('unit_price')

            if product_name and quantity and unit_price:
                ReceiptItem.objects.create(
                    receipt=receipt,
                    product_name=product_name,
                    quantity=quantity,
                    unit_price=unit_price
                )

            messages.success(request, f"Receipt #{receipt.id} created successfully!")
            return redirect('user_profile', username=request.user.username)
    else:
        form = ReceiptForm()

    return render(request, 'cash_receipts/add.html', {'form': form})


def signup(request):
    """User registration."""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('index')
    else:
        form = SignupForm()

    return render(request, 'cash_receipts/signup.html', {'form': form})