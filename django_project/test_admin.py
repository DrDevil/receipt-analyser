"""Tests for admin configuration in the cash_receipts application."""
import pytest
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from cash_receipts.admin import ReceiptAdmin, ReceiptItemAdmin
from cash_receipts.models import Receipt, ReceiptItem


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
    )


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.mark.django_db
class TestReceiptAdminConfig:
    """Tests for ReceiptAdmin configuration attributes."""

    def test_receipt_registered_in_admin(self):
        from django.contrib import admin as django_admin
        assert Receipt in django_admin.site._registry

    def test_list_display(self, admin_site):
        ma = ReceiptAdmin(Receipt, admin_site)
        assert ma.list_display == ('id', 'owner', 'total_sum', 'date', 'created_at')

    def test_list_filter(self, admin_site):
        ma = ReceiptAdmin(Receipt, admin_site)
        assert ma.list_filter == ('date', 'created_at', 'owner')

    def test_search_fields(self, admin_site):
        ma = ReceiptAdmin(Receipt, admin_site)
        assert ma.search_fields == ('owner__username', 'description')

    def test_readonly_fields(self, admin_site):
        ma = ReceiptAdmin(Receipt, admin_site)
        assert {'date', 'created_at', 'updated_at'}.issubset(set(ma.readonly_fields))

    def test_fieldsets_contain_required_sections(self, admin_site):
        ma = ReceiptAdmin(Receipt, admin_site)
        section_names = [fs[0] for fs in ma.fieldsets]
        assert 'Ownership' in section_names
        assert 'Receipt Details' in section_names
        assert 'Timestamps' in section_names

    def test_timestamps_section_is_collapsible(self, admin_site):
        ma = ReceiptAdmin(Receipt, admin_site)
        timestamps = next(fs for fs in ma.fieldsets if fs[0] == 'Timestamps')
        assert 'collapse' in timestamps[1].get('classes', ())


@pytest.mark.django_db
class TestReceiptAdminViews:
    """Tests for ReceiptAdmin HTTP views."""

    def test_changelist_accessible_to_superuser(self, client, superuser):
        client.force_login(superuser)
        response = client.get('/admin/cash_receipts/receipt/')
        assert response.status_code == 200

    def test_changelist_denied_to_regular_user(self, client, db):
        regular = User.objects.create_user(username='regular', password='pass')
        client.force_login(regular)
        response = client.get('/admin/cash_receipts/receipt/')
        assert response.status_code in (302, 403)

    def test_search_by_owner_username(self, client, superuser):
        owner = User.objects.create_user(username='receiptowner', password='pass')
        Receipt.objects.create(owner=owner, total_sum=Decimal('50.00'))
        client.force_login(superuser)
        response = client.get('/admin/cash_receipts/receipt/?q=receiptowner')
        assert response.status_code == 200
        assert b'receiptowner' in response.content


@pytest.mark.django_db
class TestReceiptItemAdminConfig:
    """Tests for ReceiptItemAdmin configuration attributes."""

    def test_receiptitem_registered_in_admin(self):
        from django.contrib import admin as django_admin
        assert ReceiptItem in django_admin.site._registry

    def test_list_display(self, admin_site):
        ma = ReceiptItemAdmin(ReceiptItem, admin_site)
        assert ma.list_display == ('id', 'receipt', 'product_name', 'quantity', 'unit_price', 'total_price')

    def test_list_filter(self, admin_site):
        ma = ReceiptItemAdmin(ReceiptItem, admin_site)
        assert ma.list_filter == ('receipt__owner', 'receipt__date')

    def test_search_fields(self, admin_site):
        ma = ReceiptItemAdmin(ReceiptItem, admin_site)
        assert ma.search_fields == ('product_name', 'receipt__owner__username')

    def test_readonly_fields(self, admin_site):
        ma = ReceiptItemAdmin(ReceiptItem, admin_site)
        assert 'total_price' in ma.readonly_fields


@pytest.mark.django_db
class TestReceiptItemAdminViews:
    """Tests for ReceiptItemAdmin HTTP views."""

    def test_changelist_accessible_to_superuser(self, client, superuser):
        client.force_login(superuser)
        response = client.get('/admin/cash_receipts/receiptitem/')
        assert response.status_code == 200

    def test_search_by_product_name(self, client, superuser):
        owner = User.objects.create_user(username='itemowner', password='pass')
        receipt = Receipt.objects.create(owner=owner, total_sum=Decimal('50.00'))
        ReceiptItem.objects.create(
            receipt=receipt,
            product_name='UniqueProduct',
            quantity=Decimal('1.00'),
            unit_price=Decimal('10.00'),
            total_price=Decimal('10.00'),
        )
        client.force_login(superuser)
        response = client.get('/admin/cash_receipts/receiptitem/?q=UniqueProduct')
        assert response.status_code == 200
        assert b'UniqueProduct' in response.content
