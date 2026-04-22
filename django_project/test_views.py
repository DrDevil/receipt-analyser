"""Tests for views in the cash_receipts application."""
import pytest
from decimal import Decimal
from django.urls import reverse
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

    @classmethod
    def create(cls, **kwargs):
        """Create a user with a set password."""
        user = super().create(**kwargs)
        user.set_password('testpass123')
        user.save()
        return user


class ReceiptFactory(factory_django.DjangoModelFactory):
    """Factory for creating test Receipt instances."""
    class Meta:
        model = Receipt
    
    owner = factory.SubFactory(UserFactory)
    total_sum = Decimal('100.00')
    description = 'Test receipt'


@pytest.mark.django_db
class TestIndexView:
    """Tests for the index view."""

    def test_index_view_accessible(self, client):
        """Test that index view is accessible."""
        response = client.get(reverse('index'))
        assert response.status_code == 200

    def test_index_view_template(self, client):
        """Test that index view uses correct template."""
        response = client.get(reverse('index'))
        assert 'cash_receipts/index.html' in [t.name for t in response.templates]

    def test_index_view_contains_receipts(self, client):
        """Test that index view displays receipts."""
        user = UserFactory()
        receipt = ReceiptFactory(owner=user)
        
        response = client.get(reverse('index'))
        assert receipt in response.context['receipts']

    def test_index_view_limits_to_10_receipts(self, client):
        """Test that index view shows only 10 most recent receipts."""
        user = UserFactory()
        for i in range(15):
            ReceiptFactory(owner=user, total_sum=Decimal(f'{i}.00'))
        
        response = client.get(reverse('index'))
        assert len(response.context['receipts']) == 10


@pytest.mark.django_db
class TestUserProfileView:
    """Tests for the user profile view."""

    def test_user_profile_accessible(self, client):
        """Test that user profile is accessible."""
        user = UserFactory(username='testuser')
        response = client.get(reverse('user_profile', args=['testuser']))
        
        assert response.status_code == 200

    def test_user_profile_shows_user_receipts(self, client):
        """Test that user profile displays user's receipts."""
        user = UserFactory(username='johndoe')
        other_user = UserFactory(username='janedoe')
        receipt1 = ReceiptFactory(owner=user)
        receipt2 = ReceiptFactory(owner=other_user)
        
        response = client.get(reverse('user_profile', args=['johndoe']))
        
        assert receipt1 in response.context['page_obj']
        assert receipt2 not in response.context['page_obj']

    def test_user_profile_404_for_nonexistent_user(self, client):
        """Test that profile for nonexistent user returns 404."""
        response = client.get(reverse('user_profile', args=['nonexistent']))
        assert response.status_code == 404

    def test_user_profile_pagination(self, client):
        """Test that user profile uses pagination."""
        user = UserFactory(username='testuser')
        for i in range(25):
            ReceiptFactory(owner=user)
        
        response = client.get(reverse('user_profile', args=['testuser']))
        
        assert response.context['page_obj'].paginator.count == 25
        assert len(response.context['page_obj']) == 20  # First page has 20 items

    def test_user_profile_template(self, client):
        """Test that user profile view uses correct template."""
        user = UserFactory(username='testuser')
        response = client.get(reverse('user_profile', args=['testuser']))
        
        assert 'cash_receipts/user.html' in [t.name for t in response.templates]


@pytest.mark.django_db
class TestAddReceiptView:
    """Tests for the add receipt view."""

    def test_add_receipt_requires_login(self, client):
        """Test that add receipt requires authentication."""
        response = client.get(reverse('add_receipt'))
        assert response.status_code == 302  # Redirect to login
        assert 'login' in response.url

    def test_add_receipt_accessible_when_logged_in(self, client, user):
        """Test that authenticated user can access add receipt form."""
        client.force_login(user)
        response = client.get(reverse('add_receipt'))
        
        assert response.status_code == 200

    def test_add_receipt_get_shows_form(self, client, user):
        """Test that GET request shows form."""
        client.force_login(user)
        response = client.get(reverse('add_receipt'))
        
        assert 'form' in response.context
        assert 'cash_receipts/add.html' in [t.name for t in response.templates]

    def test_add_receipt_post_creates_receipt(self, client, user):
        """Test that valid POST creates a receipt without items."""
        client.force_login(user)
        data = {
            'total_sum': '99.99',
            'description': 'Grocery store',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product_name': '',
            'items-0-quantity': '',
            'items-0-unit_price': '',
            'items-0-vat_amount': '',
        }
        response = client.post(reverse('add_receipt'), data)
        
        assert response.status_code == 302
        receipt = Receipt.objects.first()
        assert receipt is not None
        assert receipt.owner == user
        assert receipt.total_sum == Decimal('99.99')
        assert receipt.items.count() == 0  # Empty item should not be saved

    def test_add_receipt_with_single_item(self, client, user):
        """Test that add receipt can create receipt with single complete item."""
        client.force_login(user)
        data = {
            'total_sum': '50.00',
            'description': 'Shopping',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product_name': 'Milk',
            'items-0-quantity': '2.00',
            'items-0-unit_price': '25.00',
            'items-0-vat_amount': '5.00',
        }
        response = client.post(reverse('add_receipt'), data)
        
        assert response.status_code == 302
        receipt = Receipt.objects.first()
        assert receipt.items.count() == 1
        item = receipt.items.first()
        assert item.product_name == 'Milk'
        assert item.quantity == Decimal('2.00')
        assert item.unit_price == Decimal('25.00')
        assert item.vat_amount == Decimal('5.00')

    def test_add_receipt_with_multiple_items(self, client, user):
        """Test that add receipt can create receipt with multiple complete items."""
        client.force_login(user)
        data = {
            'total_sum': '150.00',
            'description': 'Grocery shopping',
            'items-TOTAL_FORMS': '3',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            # First item - complete
            'items-0-product_name': 'Milk',
            'items-0-quantity': '2.00',
            'items-0-unit_price': '3.50',
            'items-0-vat_amount': '1.40',
            # Second item - complete
            'items-1-product_name': 'Bread',
            'items-1-quantity': '1.00',
            'items-1-unit_price': '2.50',
            'items-1-vat_amount': '0.50',
            # Third item - empty (should be skipped)
            'items-2-product_name': '',
            'items-2-quantity': '',
            'items-2-unit_price': '',
            'items-2-vat_amount': '',
        }
        response = client.post(reverse('add_receipt'), data)
        
        assert response.status_code == 302
        receipt = Receipt.objects.first()
        assert receipt.items.count() == 2  # Only complete items saved
        
        items = list(receipt.items.all())
        assert items[0].product_name == 'Milk'
        assert items[1].product_name == 'Bread'

    def test_add_receipt_rejects_partial_data(self, client, user):
        """Test that form rejects partially filled items."""
        client.force_login(user)
        data = {
            'total_sum': '50.00',
            'description': 'Test',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product_name': 'Milk',
            'items-0-quantity': '2.00',
            'items-0-unit_price': '',  # Missing price
            'items-0-vat_amount': '',
        }
        response = client.post(reverse('add_receipt'), data)
        
        # Should return 200 with form re-displayed (not 302 redirect)
        assert response.status_code == 200
        # Receipt should NOT be created
        assert Receipt.objects.count() == 0
        # Should have error message about partial data
        messages_list = list(messages.get_messages(response.wsgi_request))
        assert any('All item fields must be filled' in str(m) for m in messages_list)

    def test_add_receipt_redirects_to_profile(self, client, user):
        """Test that successful add redirects to user profile."""
        client.force_login(user)
        data = {
            'total_sum': '75.00',
            'description': 'Test',
            'items-TOTAL_FORMS': '0',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
        }
        response = client.post(reverse('add_receipt'), data, follow=False)
        
        expected_url = reverse('user_profile', args=[user.username])
        assert response.status_code == 302
        assert expected_url in response.url


@pytest.mark.django_db
class TestSignupView:
    """Tests for the signup view."""

    def test_signup_view_accessible(self, client):
        """Test that signup view is accessible."""
        response = client.get(reverse('signup'))
        assert response.status_code == 200

    def test_signup_view_template(self, client):
        """Test that signup uses correct template."""
        response = client.get(reverse('signup'))
        assert 'cash_receipts/signup.html' in [t.name for t in response.templates]

    def test_signup_creates_user(self, client):
        """Test that valid signup data creates a user."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!'
        }
        response = client.post(reverse('signup'), data)
        
        assert response.status_code == 302
        user = User.objects.get(username='newuser')
        assert user.email == 'new@example.com'

    def test_signup_requires_email(self, client):
        """Test that email is required."""
        data = {
            'username': 'newuser',
            'email': '',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!'
        }
        response = client.post(reverse('signup'), data)
        
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()

    def test_signup_requires_matching_passwords(self, client):
        """Test that passwords must match."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123!',
            'password2': 'differentpass123!'
        }
        response = client.post(reverse('signup'), data)
        
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()

    def test_signup_logs_in_user(self, client):
        """Test that signup logs in the user."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!'
        }
        response = client.post(reverse('signup'), data, follow=True)
        
        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user.username == 'newuser'

    def test_signup_redirects_to_index(self, client):
        """Test that signup redirects to index."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!'
        }
        response = client.post(reverse('signup'), data, follow=False)
        
        assert response.status_code == 302
        assert reverse('index') in response.url


@pytest.fixture
def user(db):
    """Fixture providing a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user
