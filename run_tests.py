"""Script to run pytest tests."""
import subprocess
import sys
import os

os.chdir(r'c:\Users\Owner\Documents\git\receipt_analyser.worktrees\copilot-worktree-2026-04-21T16-59-35')
result = subprocess.run([sys.executable, '-m', 'pytest', '-v', '--tb=short'], capture_output=False)
sys.exit(result.returncode)
