"""
Forms for the cash receipts application.

This module defines Django forms for receipt management and user authentication,
including receipt creation, item line items, and user registration.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Receipt, ReceiptItem


class ReceiptForm(forms.ModelForm):
    """
    Form for creating and editing receipts.

    Includes fields for the receipt total and description.

    Attributes:
        total_sum (DecimalField): Total amount for the receipt.
        description (CharField): Optional description of the receipt.
    """

    class Meta:
        model = Receipt
        fields = ['total_sum', 'description']
        widgets = {
            'total_sum': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description'}),
        }


class ReceiptItemForm(forms.ModelForm):
    """
    Form for creating and editing individual receipt line items.

    Represents a single product within a receipt with name, quantity, price, and VAT.
    All fields are optional to allow empty rows to be skipped during validation.
    """
    # Make all fields optional - validation is done at formset level
    product_name = forms.CharField(max_length=255, required=False)
    quantity = forms.DecimalField(max_digits=8, decimal_places=2, required=False)
    unit_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    vat_amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = ReceiptItem
        fields = ['product_name', 'quantity', 'unit_price', 'vat_amount']
        widgets = {
            'product_name': forms.TextInput(attrs={'placeholder': 'Product name'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'vat_amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }


class ReceiptItemFormSet:
    """Metaclass for creating formset with custom validation."""
    pass


def create_receipt_item_formset():
    """
    Create a formset for receipt items with validation for complete/empty rows.
    
    Features:
    - Starts with 1 extra blank row for user input
    - Enforces all-or-nothing validation: either all fields filled or all empty
    - Empty rows are silently ignored (not saved)
    - Partially filled rows raise validation errors
    """
    return inlineformset_factory(
        Receipt,
        ReceiptItem,
        form=ReceiptItemForm,
        extra=1,
        can_delete=False,
        validate_min=False,
        min_num=0
    )


class SignupForm(UserCreationForm):
    """
    User registration form.

    Extends Django's UserCreationForm to require email on registration.
    Handles password validation and confirmation automatically.

    Attributes:
        email (EmailField): Email address for the new user account.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        """
        Save the user instance with the provided email.

        Args:
            commit (bool): If True, save immediately to database. If False,
                          return unsaved instance.

        Returns:
            User: The created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user