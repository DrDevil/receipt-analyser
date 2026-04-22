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
from django.core.exceptions import ValidationError
from .models import Receipt, ReceiptItem
from .forms import ReceiptForm, create_receipt_item_formset, SignupForm


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
    Handle receipt creation with multiple line items.

    Allows authenticated users to create a new receipt with multiple line items.
    Users start with one blank item row and can add more as needed. Only complete
    items (all fields filled) are saved. Partially filled items raise a validation error.

    Behavior:
    - Empty items are ignored (not saved)
    - Partially filled items raise a validation error (user must either complete or clear all fields)
    - At least the receipt itself must be valid to be created
    - Receipt is automatically associated with the logged-in user

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: On GET, renders add.html form. On POST with valid data,
                      creates receipt and items, then redirects to user profile.

    Raises:
        PermissionDenied: If user is not authenticated (handled by @login_required).
    """
    FormSet = create_receipt_item_formset()
    
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        formset = FormSet(request.POST, instance=None)
        
        if form.is_valid() and formset.is_valid():
            receipt = form.save(commit=False)
            receipt.owner = request.user
            receipt.save()
            
            # Validate and process formset
            try:
                cleaned_forms = _validate_and_clean_formset(formset)
                
                # Save only complete items
                for item_data in cleaned_forms:
                    ReceiptItem.objects.create(receipt=receipt, **item_data)
                
                messages.success(request, f"Receipt #{receipt.id} created successfully!")
                return redirect('user_profile', username=request.user.username)
            
            except ValidationError as e:
                receipt.delete()
                messages.error(request, str(e))
                # Formset will be re-displayed with the error message
        
        # If form or formset invalid, formset will be re-displayed
    else:
        form = ReceiptForm()
        formset = FormSet(instance=None)

    return render(request, 'cash_receipts/add.html', {
        'form': form,
        'formset': formset
    })


def _validate_and_clean_formset(formset):
    """
    Validate formset ensuring no partial data is saved.
    
    Rules:
    - Empty rows (all fields blank) are ignored
    - Partially filled rows raise ValidationError
    - Returns list of complete cleaned item data dicts
    
    Args:
        formset: The ReceiptItemFormSet instance (must have been validated)
        
    Returns:
        list: List of dictionaries with cleaned item data
        
    Raises:
        ValidationError: If any row has partial data
    """
    cleaned_items = []
    
    for i, form in enumerate(formset.forms):
        # Skip deleted items
        if form.cleaned_data.get('DELETE'):
            continue
        
        # Get all field values
        product_name = (form.cleaned_data.get('product_name') or '').strip()
        quantity = form.cleaned_data.get('quantity')
        unit_price = form.cleaned_data.get('unit_price')
        vat_amount = form.cleaned_data.get('vat_amount') or Decimal('0')
        
        # Count how many fields have meaningful values
        filled_fields = sum([
            bool(product_name),
            quantity is not None and quantity > 0,
            unit_price is not None and unit_price > 0
        ])
        
        # If all fields are empty, skip this row (valid - user left it blank)
        if filled_fields == 0:
            continue
        
        # If some but not all required fields are filled, raise error
        if filled_fields < 3:
            raise ValidationError(
                "All item fields must be filled: product name, quantity, and unit price "
                "are required. Leave a row completely blank to skip it."
            )
        
        # Calculate total price
        total_price = quantity * unit_price
        
        cleaned_items.append({
            'product_name': product_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price,
            'vat_amount': vat_amount
        })
    
    return cleaned_items


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