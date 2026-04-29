# Project State

## Project Overview

A Django 5.x web app for managing cash receipts with line items. Single-app structure. SQLite for development. Authentication is built-in Django auth.

## File Structure

```
receipt_analyser/
├── django_project/
│   ├── project/              # Django project config
│   │   ├── settings.py
│   │   ├── urls.py           # Root URL routing
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── cash_receipts/        # Main (only) app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py          # Both models registered
│   │   ├── apps.py
│   │   └── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   └── cash_receipts/
│   │       ├── index.html
│   │       ├── add.html
│   │       ├── user.html
│   │       ├── login.html
│   │       └── signup.html
│   ├── test_admin.py
│   ├── test_forms.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── conftest.py           # Pytest fixtures (UserFactory, ReceiptFactory, etc.)
│   ├── validate_project.py
│   └── manage.py
├── .coveragerc               # Coverage config (source=cash_receipts, omits migrations)
├── pytest.ini
├── requirements.txt
├── CLAUDE.md
├── CHANGELOG.md
├── README.md
└── TESTING_AND_DOCUMENTATION.md
```

## Core Models

### Receipt
| Field | Type | Notes |
|-------|------|-------|
| `owner` | ForeignKey(User) | CASCADE delete, related_name='receipts' |
| `total_sum` | DecimalField(10,2) | |
| `date` | DateField | auto_now_add=True |
| `description` | TextField | blank=True |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

### ReceiptItem
| Field | Type | Notes |
|-------|------|-------|
| `receipt` | ForeignKey(Receipt) | CASCADE delete, related_name='items' |
| `product_name` | CharField(255) | |
| `quantity` | DecimalField(8,2) | |
| `unit_price` | DecimalField(10,2) | |
| `total_price` | DecimalField(10,2) | Auto-calculated on save: quantity × unit_price |
| `vat_amount` | DecimalField(10,2) | default=0 |

## Forms

- **ReceiptForm** — ModelForm for Receipt; fields: `total_sum`, `description`
- **ReceiptItemForm** — ModelForm for ReceiptItem; fields: `product_name`, `quantity`, `unit_price`, `vat_amount` (all optional at form level; validated all-or-nothing in view)
- **create_receipt_item_formset()** — Factory function returning an `inlineformset_factory` (1 extra blank row, no delete, all-or-nothing validation)
- **SignupForm** — Extends `UserCreationForm`; adds required `email` field

## Views

All views are function-based.

| View | URL | Auth required |
|------|-----|---------------|
| `index` | `/` | No — shows 10 most recent receipts |
| `user_profile` | `/users/<username>/` | No — paginated (20/page) |
| `add_receipt` | `/receipts/add/` | Yes — creates receipt + inline formset items |
| `signup` | `/signup/` | No |
| `LoginView` (Django built-in) | `/login/` | No |
| `LogoutView` (Django built-in) | `/logout/` | No |

`_validate_and_clean_formset(formset)` is a private helper used by `add_receipt` to enforce all-or-nothing item row validation.

## Admin

Both models are registered with full configuration:

- **ReceiptAdmin**: `list_display`, `list_filter`, `search_fields`, `readonly_fields` (date, created_at, updated_at), collapsible Timestamps fieldset
- **ReceiptItemAdmin**: `list_display`, `list_filter`, `search_fields`, `readonly_fields` (total_price)

## URL Structure

```
/                       → index
/receipts/add/          → add_receipt (login required)
/users/<username>/      → user_profile
/signup/                → signup
/login/                 → LoginView
/logout/                → LogoutView
/admin/                 → Django admin
```

## Test Suite

Tests live in `django_project/test_*.py` and are run with pytest (see `pytest.ini`). Fixtures are in `conftest.py`.

| File | Covers | Test classes |
|------|--------|-------------|
| `test_models.py` | Receipt, ReceiptItem | TestReceipt, TestReceiptItem |
| `test_forms.py` | ReceiptForm, ReceiptItemForm, SignupForm | TestReceiptForm, TestReceiptItemForm, TestSignupForm |
| `test_views.py` | All views + formset edge cases | TestIndexView, TestUserProfileView, TestAddReceiptView, TestSignupView, TestAddReceiptFormsetEdgeCases |
| `test_admin.py` | Admin registration + HTTP access | TestReceiptAdminConfig, TestReceiptAdminViews, TestReceiptItemAdminConfig, TestReceiptItemAdminViews |

## Code Coverage

Overall: **99%**. All `cash_receipts` app files (models, views, forms, urls, admin, apps) are at **100%** individually. Migrations are excluded from coverage. Config: `.coveragerc` at repo root.

Run coverage report:
```bash
cd django_project
pytest --cov=cash_receipts --cov-report=html
# report at django_project/htmlcov/index.html
```

## Common Commands

All run from `django_project/`:

```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_views.py -v

# Run Django dev server
python manage.py runserver

# Database migrations
python manage.py makemigrations && python manage.py migrate

# Create admin superuser
python manage.py createsuperuser
```
