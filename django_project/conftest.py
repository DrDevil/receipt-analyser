"""Pytest configuration and shared fixtures for cash_receipts tests."""
import pytest
from django.contrib.auth.models import User
import factory
from factory import django as factory_django


class UserFactory(factory_django.DjangoModelFactory):
    """Factory for creating test User instances."""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.Sequence(lambda n: f'testuser{n}@example.com')
    first_name = 'Test'
    last_name = 'User'

    @classmethod
    def create(cls, **kwargs):
        """Create a user with a set password for testing."""
        user = super().create(**kwargs)
        user.set_password('testpassword123')
        user.save()
        return user


@pytest.fixture
def user(db):
    """Fixture providing a test user."""
    return UserFactory.create()


@pytest.fixture
def authenticated_client(client, user):
    """Fixture providing an authenticated test client."""
    client.force_login(user)
    return client
