# Receipt Analyzer - Testing & Documentation Guide

## Overview
This guide documents the testing and documentation setup for the Receipt Analyzer Django application.

## Testing Setup

### Dependencies
Testing dependencies in `requirements.txt`:
- **pytest** (v7.0.0+) — Test framework
- **pytest-django** (v4.5.2+) — Django plugin for pytest
- **factory-boy** (v3.2.1+) — Test data factories
- **pytest-cov** — Coverage reporting

Install with:
```bash
pip install -r requirements.txt
```

### Running Tests
All commands from `django_project/`:
```bash
# All tests
pytest -v

# Specific file
pytest test_models.py -v
pytest test_views.py -v
pytest test_forms.py -v
pytest test_admin.py -v

# With coverage
pytest --cov=cash_receipts --cov-report=html
# Report at django_project/htmlcov/index.html
```

## Test Files

### test_models.py — 11 tests
Unit tests for Receipt and ReceiptItem models.

**TestReceipt** (5 tests):
- `test_receipt_creation` — fields saved correctly
- `test_receipt_str_representation` — `__str__` output
- `test_receipt_ordering` — ordered by `created_at` descending
- `test_receipt_date_auto_set` — `date` set automatically on create
- `test_receipt_cascade_delete` — deleting receipt removes its items

**TestReceiptItem** (6 tests):
- `test_receipt_item_creation` — fields saved correctly
- `test_receipt_item_total_price_calculation` — `quantity × unit_price`
- `test_receipt_item_total_price_on_save` — recalculated when fields change
- `test_receipt_item_str_representation` — `__str__` output
- `test_receipt_item_cascade_delete` — item removed when receipt deleted
- `test_receipt_item_ordering` — ordering behaviour

---

### test_forms.py — 28 tests
Form validation and data handling.

**TestReceiptForm** (8 tests):
- Valid data, required `total_sum`, optional `description`, decimal validation, zero/large amounts, save behaviour

**TestReceiptItemForm** (9 tests):
- All four fields (`product_name`, `quantity`, `unit_price`, `vat_amount`) are optional at form level (validated all-or-nothing in the view), decimal validation, product name length limits, save behaviour

**TestSignupForm** (11 tests):
- User creation, password hashing, email requirement, password matching, weak password rejection, password-similar-to-username rejection, invalid email format, duplicate username, `commit=False` behaviour

---

### test_views.py — 32 tests
Integration tests for all views.

**TestIndexView** (4 tests):
- Accessibility, template, receipt display, 10-item limit

**TestUserProfileView** (5 tests):
- User-specific receipts, 404 for unknown user, pagination (20/page), template

**TestAddReceiptView** (8 tests):
- Login requirement, GET shows form, POST creates receipt, single item, multiple items, partial item rejected, redirect to profile

**TestSignupView** (7 tests):
- Accessibility, template, user creation, email requirement, password mismatch, auto-login after signup, redirect to index

**TestAddReceiptFormsetEdgeCases** (5 tests):
- Zero quantity rejected, zero unit price rejected, product name only rejected, receipt rolled back on partial item, complete item without VAT defaults to zero

---

### test_admin.py — 17 tests
Admin registration and HTTP-level access.

**TestReceiptAdminConfig** (7 tests):
- Receipt registered, `list_display`, `list_filter`, `search_fields`, `readonly_fields`, required fieldsets, timestamps section collapsible

**TestReceiptAdminViews** (3 tests):
- Changelist accessible to superuser, denied to regular user, search by owner username

**TestReceiptItemAdminConfig** (5 tests):
- ReceiptItem registered, `list_display`, `list_filter`, `search_fields`, `readonly_fields`

**TestReceiptItemAdminViews** (2 tests):
- Changelist accessible to superuser, search by product name

---

### Total: 88 tests

| File | Tests |
|------|------:|
| test_models.py | 11 |
| test_forms.py | 28 |
| test_views.py | 32 |
| test_admin.py | 17 |
| **Total** | **88** |

## Fixtures (conftest.py)

- **UserFactory** — `DjangoModelFactory` for `User`; sets password to `'testpassword123'` via `create()`
- **user** fixture — provides a persisted test user via `UserFactory.create()`
- **authenticated_client** fixture — `Client` already logged in as the `user` fixture

## Code Documentation

### Docstring Style
All code uses **Google-style** docstrings:
- Module-level docstring in every file
- Class docstrings with `Attributes:` section
- Function/method docstrings with `Args:`, `Returns:`, and `Raises:` sections where applicable

### Documented Files

#### cash_receipts/models.py
- **Receipt** — `owner`, `total_sum`, `date`, `description`, `created_at`, `updated_at`; ordered by `created_at` descending
- **ReceiptItem** — `receipt`, `product_name`, `quantity`, `unit_price`, `total_price` (auto-calculated), `vat_amount`; `save()` documents the auto-calculation behaviour

#### cash_receipts/views.py
- **`index()`** — 10 most recent receipts across all users
- **`user_profile()`** — paginated (20/page) receipts for one user; raises 404 for unknown username
- **`add_receipt()`** — authenticated receipt creation with inline formset; documents all-or-nothing item validation and transaction rollback behaviour
- **`_validate_and_clean_formset()`** — private helper; documents the all-or-nothing validation rules, args, and raises
- **`signup()`** — registration with auto-login on success

#### cash_receipts/forms.py
- **`ReceiptForm`** — fields: `total_sum`, `description`
- **`ReceiptItemForm`** — fields: `product_name`, `quantity`, `unit_price`, `vat_amount` (all optional at form level)
- **`create_receipt_item_formset()`** — factory function returning `inlineformset_factory`; documents 1 extra blank row, no delete, and all-or-nothing validation enforced in the view
- **`SignupForm`** — extends `UserCreationForm`; `save()` documents `commit` parameter behaviour

#### cash_receipts/admin.py
- **`ReceiptAdmin`** — `list_display` (id, owner, total_sum, date, created_at), `list_filter`, `search_fields` (username, description), `readonly_fields` (date, created_at, updated_at), collapsible Timestamps fieldset
- **`ReceiptItemAdmin`** — `list_display` (all fields + total_price), `list_filter`, `search_fields` (product name, owner), `readonly_fields` (total_price)

#### cash_receipts/urls.py
Module docstring describing URL routing.

## pytest Configuration (pytest.ini)

- Django settings module: `project.settings`
- Test discovery: `test_*.py`, `*_tests.py`, `tests.py`
- Verbose output with short tracebacks
- Custom markers: `django_db`, `slow`

## Code Coverage

Overall: **99%**. All `cash_receipts` app files individually at **100%**. Migrations excluded.

Config: `.coveragerc` at repo root — `source = cash_receipts`, omits migrations/settings/wsgi/asgi/manage.py.

## Code Quality Summary

| Area | Status |
|------|--------|
| Docstrings | All modules, classes, functions documented (Google style) |
| Test count | 88 tests across 4 files |
| Test coverage | 99% overall, 100% per app file |
| Decimal handling | Correct throughout (no float arithmetic on financial data) |
| Admin integration | Both models registered with full search/filter/readonly config |
| Authentication | `add_receipt` protected; login/logout via Django built-ins |
| Formset validation | All-or-nothing per row; rolled back on partial item |
| 404 handling | `user_profile` raises 404 for unknown username |
