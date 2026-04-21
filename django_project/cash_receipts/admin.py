"""
Django admin configuration for the cash receipts application.

Registers models with the Django admin site and configures admin display options.
"""
from django.contrib import admin
from .models import Receipt, ReceiptItem


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Receipt model.

    Displays receipt information in the admin with customizable list display,
    search, filtering, and readonly fields for audit timestamps.
    """
    list_display = ('id', 'owner', 'total_sum', 'date', 'created_at')
    list_filter = ('date', 'created_at', 'owner')
    search_fields = ('owner__username', 'description')
    readonly_fields = ('date', 'created_at', 'updated_at')
    fieldsets = (
        ('Ownership', {
            'fields': ('owner',)
        }),
        ('Receipt Details', {
            'fields': ('total_sum', 'date', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for ReceiptItem model.

    Displays receipt line items with product details and calculated totals.
    Automatically calculates total_price from quantity and unit_price.
    """
    list_display = ('id', 'receipt', 'product_name', 'quantity', 'unit_price', 'total_price')
    list_filter = ('receipt__owner', 'receipt__date')
    search_fields = ('product_name', 'receipt__owner__username')
    readonly_fields = ('total_price',)
