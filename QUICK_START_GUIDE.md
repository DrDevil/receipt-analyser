# Quick Start Guide - Receipt Analyzer

## Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
cd django_project
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser

# Run tests
pytest -v

# Start development server
python manage.py runserver
```

## Key URLs

- Homepage: `http://localhost:8000/`
- Admin: `http://localhost:8000/admin/`
- Signup: `http://localhost:8000/signup/`
- Login: `http://localhost:8000/login/`
- User Profile: `http://localhost:8000/users/<username>/`
- Add Receipt: `http://localhost:8000/receipts/add/`

## Testing Commands

```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_models.py -v

# Run specific test class
pytest test_models.py::TestReceipt -v

# Run specific test
pytest test_models.py::TestReceipt::test_receipt_creation -v

# Run with coverage
pytest --cov=cash_receipts

# Run only fast tests
pytest -m "not slow"
```

## Project Structure

```
receipt_analyser/
├── django_project/
│   ├── project/              # Main Django config
│   │   ├── settings.py       # Django settings
│   │   ├── urls.py           # Main URL routing
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── cash_receipts/        # Main app
│   │   ├── models.py         # Database models
│   │   ├── views.py          # Views
│   │   ├── forms.py          # Forms
│   │   ├── urls.py           # App URL routing
│   │   ├── admin.py          # Admin config
│   │   ├── migrations/       # Database migrations
│   │   └── tests/            # Test files (in progress)
│   ├── templates/            # HTML templates
│   ├── static/               # Static files
│   ├── manage.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_models.py        # Model tests
│   ├── test_views.py         # View tests
│   ├── test_forms.py         # Form tests
│   └── validate_project.py   # Run all tests
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── TESTING_AND_DOCUMENTATION.md
└── PROJECT_COMPLETION_SUMMARY.md
```

## Core Models

### Receipt
```python
class Receipt(models.Model):
    owner = ForeignKey(User)          # Who submitted it
    total_sum = DecimalField()        # Total amount
    date = DateField()                # Auto-set on creation
    description = TextField()         # Optional notes
    items = Relationship('ReceiptItem')  # Related items
```

### ReceiptItem
```python
class ReceiptItem(models.Model):
    receipt = ForeignKey(Receipt)     # Parent receipt
    product_name = CharField()        # Item name
    quantity = DecimalField()         # How many
    unit_price = DecimalField()       # Price per unit
    total_price = DecimalField()      # Auto-calculated
```

## Forms Available

1. **ReceiptForm** - Create receipts with optional items
2. **ReceiptItemForm** - Add individual items
3. **SignupForm** - User registration

## Views Available

1. **index()** - Homepage (10 most recent receipts)
2. **user_profile(username)** - User's receipts (paginated, 20 per page)
3. **add_receipt()** - Create new receipt (login required)
4. **signup()** - Register new user

## Common Tasks

### Run Tests
```bash
pytest -v --tb=short
```

### Check Test Coverage
```bash
pytest --cov=cash_receipts --cov-report=html
```

### Create a Receipt Programmatically
```python
from cash_receipts.models import Receipt, ReceiptItem
from django.contrib.auth.models import User

user = User.objects.get(username='john')
receipt = Receipt.objects.create(
    owner=user,
    total_sum=99.99,
    description='Grocery store'
)

item = ReceiptItem.objects.create(
    receipt=receipt,
    product_name='Milk',
    quantity=2,
    unit_price=3.50
)
# total_price auto-calculated: 2 * 3.50 = 7.00
```

### Run Django Shell
```bash
cd django_project
python manage.py shell
```

## Documentation Files

- **TESTING_AND_DOCUMENTATION.md** - Comprehensive testing and docstring guide
- **PROJECT_COMPLETION_SUMMARY.md** - Full project status and improvements
- **QUICK_START_GUIDE.md** - This file

## Need Help?

Refer to:
- Docstrings in the code (Google style)
- Test files for usage examples
- Django official documentation: https://docs.djangoproject.com/
- pytest documentation: https://docs.pytest.org/
