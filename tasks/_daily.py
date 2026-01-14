"""
Daily tasks - runs cleanup and updates site stats.
Scheduled to run once per day via python anywhere task scheduler.
"""

import os
import sys
import django
from datetime import datetime
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent.parent / 'mysite'
sys.path.insert(0, str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from cleanup import main as cleanup_main

def run_daily():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"[{timestamp}]: started daily tasks.")

    try:
        cleanup_main()
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end_timestamp}]: cleanup completed successfully.")
        return 0

    except Exception as e:
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{error_timestamp}]: error running daily tasks:")
        print(f"{str(e)}")
        return 1
    finally:
        print(f"{'='*60}")

if __name__ == "__main__":
    exit_code = run_daily()

    if exit_code != 0:
        sys.exit(exit_code)
