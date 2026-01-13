import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append("/home/benjaminbbonnell/mysite")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from collector import main as collector_main
from pivot import main as pivot_main
from analysis import main as analysis_main

def run_hourly():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"[{timestamp}]: started daily tasks.")

    try:
        collector_main()
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end_timestamp}]: collected weather data successfully.")

        pivot_main()
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end_timestamp}]: pivot complete successfully.")

        analysis_main()
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end_timestamp}]: analysis complete successfully.")

        return 0

    except Exception as e:
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{error_timestamp}]: error running weather collection and analysis:")
        print(f"{str(e)}")

    finally:
        print(f"{'='*60}")

if __name__ == "__main__":
    exit_code = run_hourly()

    if exit_code != 0:
        sys.exit(exit_code)