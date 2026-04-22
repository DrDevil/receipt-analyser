"""Tests for forms in the cash_receipts application."""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from cash_receipts.forms import ReceiptForm, ReceiptItemForm, SignupForm
from cash_receipts.models import Receipt, ReceiptItem


@pytest.mark.django_db
class TestReceiptForm:
    """Tests for the ReceiptForm."""

    def test_receipt_form_valid_data(self):
        """Test that ReceiptForm is valid with correct data."""
        form = ReceiptForm(data={
            'total_sum': '99.99',
            'description': 'Grocery shopping'
        })
        assert form.is_valid()

    def test_receipt_form_requires_total_sum(self):
        """Test that total_sum is required."""
        form = ReceiptForm(data={
            'description': 'Test',
            'total_sum': ''
        })
        assert not form.is_valid()

    def test_receipt_form_accepts_optional_fields(self):
        """Test that product fields are optional."""
        form = ReceiptForm(data={
            'total_sum': '50.00',
            'description': 'Test'
        })
        assert form.is_valid()

    def test_receipt_form_partial_product_data(self):
        """Test form with partial product data (some fields missing)."""
        form = ReceiptForm(data={
            'total_sum': '50.00',
            'description': 'Test',
            'product_name': 'Milk',
            'quantity': '',
            'unit_price': '5.00'
        })
        assert form.is_valid()

    def test_receipt_form_decimal_validation(self):
        """Test that invalid decimal values are rejected."""
        form = ReceiptForm(data={
            'total_sum': 'not-a-number',
            'description': 'Test'
        })
        assert not form.is_valid()

    def test_receipt_form_save_creates_instance(self):
        """Test that form.save() creates a Receipt instance."""
        form = ReceiptForm(data={
            'total_sum': '75.50',
            'description': 'Test receipt'
        })
        assert form.is_valid()
        receipt = form.save(commit=False)
        
        assert isinstance(receipt, Receipt)
        assert receipt.total_sum == Decimal('75.50')
        assert receipt.description == 'Test receipt'

    def test_receipt_form_zero_amount(self):
        """Test form with zero amount."""
        form = ReceiptForm(data={
            'total_sum': '0.00',
            'description': 'Free item'
        })
        assert form.is_valid()

    def test_receipt_form_large_amount(self):
        """Test form with large amount."""
        form = ReceiptForm(data={
            'total_sum': '99999.99',
            'description': 'Expensive purchase'
        })
        assert form.is_valid()


@pytest.mark.django_db
class TestReceiptItemForm:
    """Tests for the ReceiptItemForm."""

    def test_receipt_item_form_valid_data(self):
        """Test that ReceiptItemForm is valid with correct data."""
        form = ReceiptItemForm(data={
            'product_name': 'Apple',
            'quantity': '5.00',
            'unit_price': '1.50',
            'vat_amount': '0.75'
        })
        assert form.is_valid()

    def test_receipt_item_form_product_name_optional(self):
        """Test that product_name is optional at form level (formset handles all-or-nothing validation)."""
        form = ReceiptItemForm(data={
            'product_name': '',
            'quantity': '5.00',
            'unit_price': '1.50',
            'vat_amount': '0.00'
        })
        assert form.is_valid()

    def test_receipt_item_form_quantity_optional(self):
        """Test that quantity is optional at form level (formset handles all-or-nothing validation)."""
        form = ReceiptItemForm(data={
            'product_name': 'Apple',
            'quantity': '',
            'unit_price': '1.50',
            'vat_amount': '0.00'
        })
        assert form.is_valid()

    def test_receipt_item_form_unit_price_optional(self):
        """Test that unit_price is optional at form level (formset handles all-or-nothing validation)."""
        form = ReceiptItemForm(data={
            'product_name': 'Apple',
            'quantity': '5.00',
            'unit_price': '',
            'vat_amount': '0.00'
        })
        assert form.is_valid()

    def test_receipt_item_form_vat_optional(self):
        """Test that vat_amount is optional."""
        form = ReceiptItemForm(data={
            'product_name': 'Apple',
            'quantity': '5.00',
            'unit_price': '1.50',
            'vat_amount': ''
        })
        assert form.is_valid()

    def test_receipt_item_form_decimal_validation(self):
        """Test decimal field validation."""
        form = ReceiptItemForm(data={
            'product_name': 'Apple',
            'quantity': 'invalid',
            'unit_price': '1.50',
            'vat_amount': '0.00'
        })
        assert not form.is_valid()

    def test_receipt_item_form_save_creates_instance(self):
        """Test that form.save() creates ReceiptItem instance."""
        form = ReceiptItemForm(data={
            'product_name': 'Banana',
            'quantity': '3.00',
            'unit_price': '0.99',
            'vat_amount': '0.30'
        })
        assert form.is_valid()
        item = form.save(commit=False)
        
        assert isinstance(item, ReceiptItem)
        assert item.product_name == 'Banana'
        assert item.quantity == Decimal('3.00')
        assert item.unit_price == Decimal('0.99')
        assert item.vat_amount == Decimal('0.30')

    def test_receipt_item_form_long_product_name(self):
        """Test form with maximum length product name."""
        long_name = 'A' * 255
        form = ReceiptItemForm(data={
            'product_name': long_name,
            'quantity': '1.00',
            'unit_price': '10.00',
            'vat_amount': '0.00'
        })
        assert form.is_valid()

    def test_receipt_item_form_exceeds_max_product_name(self):
        """Test form with product name exceeding max length."""
        long_name = 'A' * 256
        form = ReceiptItemForm(data={
            'product_name': long_name,
            'quantity': '1.00',
            'unit_price': '10.00',
            'vat_amount': '0.00'
        })
        assert not form.is_valid()


@pytest.mark.django_db
class TestSignupForm:
    """Tests for the SignupForm."""

    def test_signup_form_valid_data(self):
        """Test that SignupForm is valid with correct data."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert form.is_valid()

    def test_signup_form_requires_username(self):
        """Test that username is required."""
        form = SignupForm(data={
            'username': '',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert not form.is_valid()

    def test_signup_form_requires_email(self):
        """Test that email is required (custom requirement)."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': '',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert not form.is_valid()

    def test_signup_form_requires_passwords(self):
        """Test that both password fields are required."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '',
            'password2': 'SecurePass123!'
        })
        assert not form.is_valid()

    def test_signup_form_passwords_must_match(self):
        """Test that passwords must match."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!'
        })
        assert not form.is_valid()

    def test_signup_form_weak_password(self):
        """Test that weak passwords are rejected."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '123',
            'password2': '123'
        })
        assert not form.is_valid()

    def test_signup_form_password_too_similar_to_username(self):
        """Test that password similar to username is rejected."""
        form = SignupForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testuser123',
            'password2': 'testuser123'
        })
        assert not form.is_valid()

    def test_signup_form_invalid_email_format(self):
        """Test that invalid email is rejected."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'not-an-email',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert not form.is_valid()

    def test_signup_form_save_creates_user(self):
        """Test that form.save() creates a User instance."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert form.is_valid()
        user = form.save()
        
        assert isinstance(user, User)
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'

    def test_signup_form_save_hashes_password(self):
        """Test that password is properly hashed."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert form.is_valid()
        user = form.save()
        
        # Password should not be plain text
        assert user.password != 'SecurePass123!'
        # But should authenticate
        assert user.check_password('SecurePass123!')

    def test_signup_form_save_with_commit_false(self):
        """Test form.save(commit=False) returns unsaved user."""
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert form.is_valid()
        user = form.save(commit=False)
        
        assert isinstance(user, User)
        assert not User.objects.filter(username='newuser').exists()
        
        # Save manually
        user.save()
        assert User.objects.filter(username='newuser').exists()

    def test_signup_form_duplicate_username(self):
        """Test that duplicate username is rejected."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        form = SignupForm(data={
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert not form.is_valid()
