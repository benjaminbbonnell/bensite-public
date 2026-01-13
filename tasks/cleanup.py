import os
import sys
import django
import time
from django.db import connection
from django.db import transaction
from django.conf import settings
import psycopg2


sys.path.append("/home/benjaminbbonnell/mysite")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"
django.setup()

from weather.models import ForecastPivot, SiteStats

sqldbname = os.environ.get('SQLDBNAME')
sqlhost = os.environ.get('SQLHOST')
sqluser = os.environ.get('SQLUSER')
sqlpassword = os.environ.get('SQLPASSWORD')
sqlport = os.environ.get('SQLPORT')

threshold_setting = settings.OLD_FORECAST_THRESHOLD
current_time = round((int(time.time())) / 3600) * 3600
threshold_epoch = current_time - (threshold_setting * 86400)


def total_forecasts():
    total_forecast_count = ForecastPivot.objects.count()
    countdata = {'stat': total_forecast_count}

    try:
        with transaction.atomic():
            SiteStats.objects.update_or_create(
                name='total_forecast_count',
                defaults=countdata
            )
            print(f"Total_forecast_count was updated, the new count is: {total_forecast_count}")
    except Exception as e:
        print(f"error updating total_forecast_count: {e}")
    finally:
        connection.close()

def delete_old_forecasts(threshold):

    query = 'DELETE FROM weather_forecastdata WHERE forecast_made < %s;'

    conn = psycopg2.connect(dbname = sqldbname,
                host = sqlhost,
                user = sqluser,
                password = sqlpassword,
                port = sqlport)
    cursor = conn.cursor()

    try:
        start_time = time.time()
        cursor.execute(query, [threshold])
        rows_deleted = cursor.rowcount
        formatted_rows = f"{rows_deleted:,}"
        conn.commit()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Query complete in {execution_time:.2f} seconds. Deleted {formatted_rows} rows.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

def main():
    total_forecasts()
    delete_old_forecasts(threshold_epoch)

if __name__ == "__main__":
    main()