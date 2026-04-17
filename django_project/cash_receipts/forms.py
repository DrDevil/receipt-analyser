from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Receipt, ReceiptItem


class ReceiptForm(forms.ModelForm):
    """Form for creating/editing a receipt."""
    # Inline items will be handled via formset
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
    """Form for a single receipt line item."""
    class Meta:
        model = ReceiptItem
        fields = ['product_name', 'quantity', 'unit_price']


class SignupForm(UserCreationForm):
    """User registration form."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user