# Receipt Analyzer ###

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

# Requirements

## Requirements for v1.0 (Basic functionality):

### UI:

1. The user should be able to access the app webpage :white_check_mark:
2. User should be able to register :white_check_mark:
3. User should be able to login :white_check_mark:
4. User should be able to filter cash receipts by users :white_check_mark:
5. User should be able to see all cash receipts in the system :white_check_mark:

### Backend:

6. Basic db configuration to accomodate user and receipt models in 1 to many relation. :white_check_mark:


## Requirements for v1.1 (Extended functionality):

### UI:

9. User should be able to search cash receits by keyword - E.g tomatos return all cash receits containing tomatos
10. User should be able to submit multiple line items per cash receipt. ISSUE [#5](https://github.com/DrDevil/receipt-analyser/issues/5)
11. User should be able to select which curency is being used for the receipt. ISSUE [#6](https://github.com/DrDevil/receipt-analyser/issues/6)

### Backend:

10. Configuration of elastic search
11. Basic OCR setup
12. Relate entries for goods and prices to the submitter of the receipt.

## Requirements for v2.0 (OCR enabled):

### UI:

7. User should be able to upload a photo of a cash reciet
8. User should see summary of the purchase from the cash receit after succesfull upload

### Backend:
