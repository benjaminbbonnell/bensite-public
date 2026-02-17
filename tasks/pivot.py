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


# this should probably be moved to the view at some point but the processing to do it there may not be worth it
# dividing by 3600 changes from seconds to hours in epoch time. The forecasts are normalized to the nearest hours when they're collected already so should always result in a neat number of hours

queries = {
    "pivot": '''
    WITH current AS (
        SELECT
            MAX(forecast_made) AS current
        FROM weather_forecastdata
    ),
    currenttemps AS (
        SELECT
            city_id,
            api_name,
            temp_f AS currenttemp,
            precip_in AS current_precip_in,
            precip_prob AS current_precip_prob
        FROM weather_forecastdata, current
        WHERE forecast_made = current.current AND forecast_epoch = current.current
    ),
    forecast_data AS (
        SELECT
            city,
            city_id,
            api_name,
            forecast_made,
            forecast_epoch,
            temp_f,
            precip_in AS forecasted_precip_in,
            precip_prob AS forecasted_precip_prob,
            (current - forecast_made) / 3600 AS hoursbefore
        FROM weather_forecastdata CROSS JOIN current
    )

    INSERT INTO weather_forecastpivot(api_name, city_name, city_id, forecast_made, forecast_epoch, currenttemp, temp_f, current_precip_in, current_precip_prob, forecasted_precip_in, forecasted_precip_prob, hoursbefore)

    SELECT
        forecast_data.api_name,
        forecast_data.city AS city_name,
        forecast_data.city_id,
        forecast_made,
        forecast_epoch,
        currenttemps.currenttemp,
        forecast_data.temp_f,
        currenttemps.current_precip_in,
        currenttemps.current_precip_prob,
        forecast_data.forecasted_precip_in,
        forecast_data.forecasted_precip_prob,
        forecast_data.hoursbefore

        FROM forecast_data
        JOIN currenttemps ON forecast_data.city_id = currenttemps.city_id AND forecast_data.api_name = currenttemps.api_name
        WHERE forecast_data.forecast_epoch = (SELECT current FROM current);
    ''',
    "ensemblepivot": '''
    WITH current AS (
        SELECT
        MAX(forecast_made) AS current
    FROM weather_forecastdata
    ),
    currenttemps AS (
        SELECT
            city_id,
            api_name,
            temp_f AS currenttemp,
            precip_in AS current_precip_in,
            precip_prob AS current_precip_prob
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
            precip_in AS forecasted_precip_in,
            precip_prob AS forecasted_precip_prob,
            (current - forecast_made) / 3600 AS hoursbefore
        FROM weather_forecastdata, current
    )

    INSERT INTO weather_forecastpivot(api_name, city_name, city_id, forecast_made, forecast_epoch, currenttemp, temp_f, current_precip_in, current_precip_prob, forecasted_precip_in, forecasted_precip_prob, hoursbefore)

    SELECT
        'ensemble' AS api_name,
        forecast_data.city AS city_name,
        forecast_data.city_id,
        forecast_made,
        forecast_epoch,
        ROUND(AVG(currenttemps.currenttemp), 2),
        ROUND(AVG(forecast_data.temp_f), 2),
        ROUND(AVG(currenttemps.current_precip_in), 2),
        ROUND(AVG(currenttemps.current_precip_prob), 2),
        ROUND(AVG(forecast_data.forecasted_precip_in), 2),
        ROUND(AVG(forecast_data.forecasted_precip_prob), 2),
        forecast_data.hoursbefore
        FROM forecast_data
        JOIN currenttemps ON forecast_data.city_id = currenttemps.city_id AND forecast_data.api_name = currenttemps.api_name
        WHERE forecast_data.forecast_epoch = (SELECT current FROM current) AND hoursbefore < 72
        GROUP BY forecast_data.city, forecast_data.city_id, forecast_made, forecast_epoch, forecast_data.hoursbefore;
    ''',
    "pivotv2": '''
        WITH last_hour AS (
        SELECT MAX(time_epoch) AS last_hour_time
        FROM weather_historicaldata
        )

        INSERT INTO weather_forecastpivotv2(api_name, city_id, city_name, forecast_made, forecast_epoch, currenttemp, temp_f, hoursbefore, current_precip_in, current_precip_prob, forecasted_precip_in, forecasted_precip_prob)

        SELECT 
            weather_forecastdata.api_name, 
            weather_forecastdata.city_id, 
            weather_forecastdata.city,
            weather_forecastdata.forecast_made, 
            weather_forecastdata.forecast_epoch,
            weather_historicaldata.temp_f AS currenttemp,
            weather_forecastdata.temp_f,
            (weather_forecastdata.forecast_epoch - weather_forecastdata.forecast_made) / 3600 AS hoursbefore,
            weather_forecastdata.precip_in AS forecasted_precip_in, 
            weather_forecastdata.precip_prob AS forecasted_precip_prob, 
            weather_forecastdata.precip_in AS current_precip_in,
            weather_historicaldata.precip_prob AS current_precip_prob

        FROM
            weather_forecastdata
        LEFT JOIN
            weather_historicaldata
        ON
            weather_forecastdata.city_id = weather_historicaldata.city_id AND
            weather_forecastdata.forecast_epoch = weather_historicaldata.time_epoch
        WHERE
            weather_forecastdata.forecast_epoch IN (SELECT last_hour_time FROM last_hour)
    '''
}

def execsql(query):
    conn = psycopg2.connect(dbname = sqldbname,
                host = sqlhost,
                user = sqluser,
                password = sqlpassword,
                port = sqlport)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        conn.commit()
        print("query complete.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

def main():
    for query_name, query in queries.items():
        print(f"executing {query_name}.")
        execsql(query)

if __name__ == "__main__":
    main()