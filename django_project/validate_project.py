"""
Comprehensive validation script for Receipt Analyzer project.
Runs all tests and reports results.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.insert(0, str(Path(__file__).parent / 'django_project'))

django.setup()

# Now run pytest
import pytest

# Run all tests
exit_code = pytest.main([
    'test_models.py',
    'test_views.py', 
    'test_forms.py',
    '-v',
    '--tb=short',
    '--color=yes'
])

if exit_code == 0:
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED - Project is ready for next features!")
    print("="*70)
else:
    print("\n" + "="*70)
    print(f"✗ {exit_code} test failures - Review output above")
    print("="*70)

sys.exit(exit_code)
