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

queries = {
    "hoursbeforechart": '''
        INSERT INTO weather_hoursbeforechart(api_name, avg_dif, signed_dif, hoursbefore, forecast_pivot_version)
        SELECT 
            api_name, 
            ROUND(AVG(ABS(currenttemp - temp_f)), 2) AS avg_dif, 
            ROUND(AVG(currenttemp - temp_f), 2) AS signed_dif, 
            hoursbefore, 
            2 AS forecast_pivot_version
        FROM 
            weather_forecastpivotv2
        GROUP BY 
            api_name, hoursbefore
        ORDER BY 
            hoursbefore, api_name;
    ''',
    "monthlyaveragechart": '''
        INSERT INTO weather_monthlyaveragechart(api_name, month, avg_dif, hoursbefore, forecast_pivot_version)
        SELECT
            api_name,
            to_char(to_timestamp(forecast_made), 'MM')::int as month,
            ROUND(AVG(ABS(currenttemp - temp_f)), 2) AS avg_dif,
            hoursbefore,
            2 AS forecast_pivot_version
        FROM
            weather_forecastpivotv2
        WHERE
            hoursbefore IN (1, 6, 12, 24)
        GROUP BY
            api_name, month, hoursbefore;
    ''',
    "precipitationprobchart" : '''
        WITH forecast_counts AS (
        SELECT 
            api_name, 
            hoursbefore, 
            FLOOR(forecasted_precip_prob / 10) * 10 AS forecast_prob_bucket, 
            COUNT(*) AS forecasted_count
        FROM weather_forecastpivotv2
        WHERE hoursbefore IN (1,6,12,24) AND forecasted_precip_prob IS NOT NULL
        GROUP BY api_name, FLOOR(forecasted_precip_prob / 10) * 10, hoursbefore
        ),
        actual_counts AS (
            SELECT 
                api_name, 
                hoursbefore, 
                FLOOR(forecasted_precip_prob / 10) * 10 AS forecast_prob_bucket, 
                COUNT(*) AS actual_count
            FROM weather_forecastpivotv2
            WHERE hoursbefore IN (1,6,12,24) 
                AND forecasted_precip_prob IS NOT NULL 
                AND (current_precip_in > 0.00 OR current_precip_prob >= 60)
            GROUP BY api_name, FLOOR(forecasted_precip_prob / 10) * 10, hoursbefore
        )

        INSERT INTO
            weather_precipprobchart(api_name, hoursbefore, forecast_prob_bucket, actual_percentage, forecasted_count, actual_count, forecast_pivot_version)

        SELECT
            forecast_counts.api_name, 
            forecast_counts.hoursbefore, 
            forecast_counts.forecast_prob_bucket, 
            ROUND(COALESCE(actual_counts.actual_count::numeric / NULLIF(forecast_counts.forecasted_count::numeric, 0) * 100, 0), 2) AS actual_percentage,	
            forecast_counts.forecasted_count,
            COALESCE(actual_counts.actual_count, 0) AS actual_count,
            2 AS forecast_pivot_version
        FROM 
            forecast_counts
        LEFT JOIN 
            actual_counts
        ON 
            forecast_counts.api_name = actual_counts.api_name
            AND forecast_counts.hoursbefore = actual_counts.hoursbefore
            AND forecast_counts.forecast_prob_bucket = actual_counts.forecast_prob_bucket
        ORDER BY forecast_counts.api_name, forecast_counts.forecast_prob_bucket;'''
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