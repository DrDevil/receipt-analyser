"""
Forms for the cash receipts application.

This module defines Django forms for receipt management and user authentication,
including receipt creation, item line items, and user registration.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Receipt, ReceiptItem


class ReceiptForm(forms.ModelForm):
    """
    Form for creating and editing receipts.

    Includes fields for the receipt total and description, plus optional
    fields for adding a single line item (product) during creation.

    Attributes:
        product_name (CharField): Optional name of the product in the receipt.
        quantity (DecimalField): Optional quantity of the product.
        unit_price (DecimalField): Optional unit price of the product.
    """
    product_name = forms.CharField(max_length=255, required=False, label="Product Name")
    quantity = forms.DecimalField(max_digits=8, decimal_places=2, required=False, label="Quantity")
    unit_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Unit Price")

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

    Represents a single product within a receipt with name, quantity, and price.
    """
    class Meta:
        model = ReceiptItem
        fields = ['product_name', 'quantity', 'unit_price']


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