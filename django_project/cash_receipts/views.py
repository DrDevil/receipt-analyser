"""
Views for the cash receipts application.

This module contains all view functions for the cash receipts application,
including homepage, user profiles, receipt management, and authentication.
"""
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Receipt, ReceiptItem
from .forms import ReceiptForm, SignupForm


def index(request):
    """
    Display the homepage with recent receipts.

    Shows the 10 most recent receipts across all users. This serves as the
    landing page and gives visitors an overview of recent activity.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered index.html template with recent receipts.
    """
    receipts_list = Receipt.objects.all()[:10]
    return render(request, 'cash_receipts/index.html', {
        'receipts': receipts_list
    })


def user_profile(request, username):
    """
    Display all receipts for a specific user.

    Shows a paginated list of all receipts submitted by the user.
    Each page displays 20 receipts in reverse chronological order.

    Args:
        request (HttpRequest): The HTTP request object.
        username (str): The username of the user whose profile to display.

    Returns:
        HttpResponse: Rendered user.html template with user's receipts.

    Raises:
        Http404: If the specified user does not exist.
    """
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
    """
    Handle receipt creation.

    Allows authenticated users to create a new receipt with an optional
    line item (product). The receipt is automatically associated with
    the logged-in user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: On GET, renders add.html form. On POST with valid data,
                      creates receipt and redirects to user profile.

    Raises:
        PermissionDenied: If user is not authenticated (handled by @login_required).
    """
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.owner = request.user
            receipt.save()

            # Handle optional line item
            product_name = request.POST.get('product_name')
            quantity = request.POST.get('quantity')
            unit_price = request.POST.get('unit_price')

            if product_name and quantity and unit_price:
                ReceiptItem.objects.create(
                    receipt=receipt,
                    product_name=product_name,
                    quantity=Decimal(quantity),
                    unit_price=Decimal(unit_price)
                )

            messages.success(request, f"Receipt #{receipt.id} created successfully!")
            return redirect('user_profile', username=request.user.username)
    else:
        form = ReceiptForm()

    return render(request, 'cash_receipts/add.html', {'form': form})


def signup(request):
    """
    Handle user registration.

    Allows new users to create an account. Upon successful registration,
    the user is automatically logged in and redirected to the homepage.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: On GET, renders signup.html form. On POST with valid data,
                      creates user, logs them in, and redirects to index.
    """
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