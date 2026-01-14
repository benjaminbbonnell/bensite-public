import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the mysite directory
env_path = Path(__file__).resolve().parent.parent / 'mysite' / '.env'
load_dotenv(dotenv_path=env_path)

sqldbname = os.environ.get('SQLDBNAME')
sqlhost = os.environ.get('SQLHOST')
sqluser = os.environ.get('SQLUSER')
sqlpassword = os.environ.get('SQLPASSWORD')
sqlport = os.environ.get('SQLPORT')

def runpivot():
    sql = '''WITH current AS (
    SELECT
        MAX(forecast_made) AS current
    FROM weather_forecastdata
    ),
    currenttemps AS (
        SELECT
	        city_id,
	        api_name,
	        temp_f AS currenttemp
        FROM weather_forecastdata
        WHERE forecast_made = (SELECT current FROM current) AND forecast_epoch = (SELECT current FROM current)
    ),
    forecast_data AS (
        SELECT
            city,
            city_id,
            api_name,
            forecast_made,
            forecast_epoch,
            temp_f,
            (current - forecast_made) / 3600 AS hoursbefore
        FROM weather_forecastdata, current
    )

    INSERT INTO weather_forecastpivot(api_name, city_name, city_id, forecast_made, forecast_epoch, currenttemp, temp_f, hoursbefore)

    SELECT
        forecast_data.api_name,
        forecast_data.city AS city_name,
	    forecast_data.city_id,
        forecast_made,
        forecast_epoch,
        currenttemps.currenttemp,
        forecast_data.temp_f,
        forecast_data.hoursbefore
        FROM forecast_data
        JOIN currenttemps ON forecast_data.city_id = currenttemps.city_id AND forecast_data.api_name = currenttemps.api_name
        WHERE forecast_data.forecast_epoch = (SELECT current FROM current);'''

    conn = psycopg2.connect(dbname = sqldbname,
                    host = sqlhost,
                    user = sqluser,
                    password = sqlpassword,
                    port = sqlport)
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        conn.commit()
        print("pivot complete.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()

    cursor.close()
    conn.close()

def main():
    runpivot()

if __name__ == "__main__":
    main()





