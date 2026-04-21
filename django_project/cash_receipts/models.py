"""
Models for the cash receipts application.

This module defines the data models for managing cash receipts and their line items.
It provides Receipt and ReceiptItem models to track purchases and individual items.
"""
from django.db import models
from django.contrib.auth.models import User


class Receipt(models.Model):
    """
    Represents a cash receipt document.

    A Receipt is the main entity that represents a single cash purchase transaction.
    It belongs to a User and contains multiple line items (products purchased).

    Attributes:
        owner (ForeignKey): The User who owns/submitted this receipt.
        total_sum (DecimalField): Total amount spent in this receipt.
        date (DateField): Date when the receipt was created (auto-set on creation).
        description (TextField): Optional notes or description about the receipt.
        created_at (DateTimeField): Timestamp when the record was created.
        updated_at (DateTimeField): Timestamp when the record was last modified.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipts')
    total_sum = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return a readable string representation of the receipt."""
        return f"Receipt #{self.id} - ${self.total_sum}"


class ReceiptItem(models.Model):
    """
    Represents a single line item (product) within a receipt.

    Each ReceiptItem represents one product purchased as part of a receipt.
    The total_price is automatically calculated from quantity and unit_price.

    Attributes:
        receipt (ForeignKey): The Receipt this item belongs to.
        product_name (CharField): Name/description of the product.
        quantity (DecimalField): Number of units purchased.
        unit_price (DecimalField): Price per unit.
        total_price (DecimalField): Total price for this line (quantity * unit_price).
        vat_amount (DecimalField): Value Added Tax amount for this line item.
    """
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        """Return a readable string representation of the receipt item."""
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        """
        Save the receipt item, automatically calculating total_price.

        This method ensures that total_price is always calculated as quantity
        multiplied by unit_price before saving to maintain data consistency.
        """
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)