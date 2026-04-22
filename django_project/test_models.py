"""Unit tests for models in the cash_receipts application."""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from cash_receipts.models import Receipt, ReceiptItem
import factory
from factory import django as factory_django


class UserFactory(factory_django.DjangoModelFactory):
    """Factory for creating test User instances."""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')


class ReceiptFactory(factory_django.DjangoModelFactory):
    """Factory for creating test Receipt instances."""
    class Meta:
        model = Receipt
    
    owner = factory.SubFactory(UserFactory)
    total_sum = Decimal('100.00')
    description = 'Test receipt'


class ReceiptItemFactory(factory_django.DjangoModelFactory):
    """Factory for creating test ReceiptItem instances."""
    class Meta:
        model = ReceiptItem
    
    receipt = factory.SubFactory(ReceiptFactory)
    product_name = 'Test Product'
    quantity = Decimal('1.00')
    unit_price = Decimal('50.00')
    vat_amount = Decimal('5.00')


@pytest.mark.django_db
class TestReceipt:
    """Tests for the Receipt model."""

    def test_receipt_creation(self):
        """Test basic receipt creation."""
        user = UserFactory()
        receipt = ReceiptFactory(owner=user, total_sum=Decimal('150.00'))
        
        assert receipt.id is not None
        assert receipt.owner == user
        assert receipt.total_sum == Decimal('150.00')
        assert receipt.description == 'Test receipt'

    def test_receipt_str_representation(self):
        """Test Receipt __str__ method."""
        receipt = ReceiptFactory(total_sum=Decimal('99.99'))
        expected = f"Receipt #{receipt.id} - $99.99"
        assert str(receipt) == expected

    def test_receipt_ordering(self):
        """Test that receipts are ordered by creation date (newest first)."""
        user = UserFactory()
        receipt1 = ReceiptFactory(owner=user)
        receipt2 = ReceiptFactory(owner=user)
        
        receipts = Receipt.objects.all()
        # Should be in reverse chronological order (newest first)
        assert receipts[0].created_at >= receipts[1].created_at

    def test_receipt_date_auto_set(self):
        """Test that receipt date is automatically set."""
        receipt = ReceiptFactory()
        assert receipt.date is not None

    def test_receipt_cascade_delete(self):
        """Test that deleting user cascades to their receipts."""
        user = UserFactory()
        receipt = ReceiptFactory(owner=user)
        receipt_id = receipt.id
        
        user.delete()
        
        assert not Receipt.objects.filter(id=receipt_id).exists()


@pytest.mark.django_db
class TestReceiptItem:
    """Tests for the ReceiptItem model."""

    def test_receipt_item_creation(self):
        """Test basic receipt item creation."""
        receipt = ReceiptFactory()
        item = ReceiptItemFactory(receipt=receipt, quantity=Decimal('2.00'), unit_price=Decimal('25.00'))
        
        assert item.id is not None
        assert item.receipt == receipt
        assert item.product_name == 'Test Product'
        assert item.quantity == Decimal('2.00')
        assert item.unit_price == Decimal('25.00')

    def test_receipt_item_total_price_calculation(self):
        """Test that total_price is calculated correctly."""
        item = ReceiptItemFactory(quantity=Decimal('3.00'), unit_price=Decimal('10.50'))
        
        expected_total = Decimal('3.00') * Decimal('10.50')
        assert item.total_price == expected_total

    def test_receipt_item_total_price_on_save(self):
        """Test that total_price is recalculated on save."""
        item = ReceiptItemFactory(quantity=Decimal('2.00'), unit_price=Decimal('50.00'))
        original_total = item.total_price
        
        # Modify quantities and save
        item.quantity = Decimal('5.00')
        item.unit_price = Decimal('30.00')
        item.save()
        
        new_total = Decimal('5.00') * Decimal('30.00')
        assert item.total_price == new_total
        assert item.total_price != original_total

    def test_receipt_item_str_representation(self):
        """Test ReceiptItem __str__ method."""
        item = ReceiptItemFactory(product_name='Apples', quantity=Decimal('2.50'))
        assert str(item) == 'Apples x2.50'

    def test_receipt_item_cascade_delete(self):
        """Test that deleting receipt cascades to its items."""
        receipt = ReceiptFactory()
        item = ReceiptItemFactory(receipt=receipt)
        item_id = item.id
        
        receipt.delete()
        
        assert not ReceiptItem.objects.filter(id=item_id).exists()

    def test_receipt_item_ordering(self):
        """Test that receipt items are ordered by id."""
        receipt = ReceiptFactory()
        item1 = ReceiptItemFactory(receipt=receipt)
        item2 = ReceiptItemFactory(receipt=receipt)
        
        items = receipt.items.all()
        assert items[0].id <= items[1].id
