import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / 'mysite' / '.env'
load_dotenv(dotenv_path=env_path)

sqldbname = os.environ.get('SQLDBNAME')
sqlhost = os.environ.get('SQLHOST')
sqluser = os.environ.get('SQLUSER')
sqlpassword = os.environ.get('SQLPASSWORD')
sqlport = os.environ.get('SQLPORT')


# to-do: merge analysis v1 and v2 with UNION

queries = {
    "hoursbeforechart": '''
        TRUNCATE weather_hoursbeforechart RESTART IDENTITY;

        INSERT INTO weather_hoursbeforechart(api_name, avg_dif, signed_dif, hoursbefore, forecast_pivot_version)
        SELECT 
            api_name, 
            ROUND(AVG(ABS(currenttemp - temp_f)), 2) AS avg_dif, 
            ROUND(AVG(currenttemp - temp_f), 2) AS signed_dif, 
            hoursbefore, 
            1 AS forecast_pivot_version
        FROM 
            weather_forecastpivot
        GROUP BY 
            api_name, hoursbefore
        ORDER BY 
            hoursbefore, api_name;
    ''',
    "monthlyaveragechart": '''
        TRUNCATE weather_monthlyaveragechart RESTART IDENTITY;

        INSERT INTO weather_monthlyaveragechart(api_name, month, avg_dif, hoursbefore, forecast_pivot_version)
        SELECT
            api_name,
            to_char(to_timestamp(forecast_made), 'MM')::int as month,
            ROUND(AVG(ABS(currenttemp - temp_f)), 2) AS avg_dif,
            hoursbefore,
            1 AS forecast_pivot_version
        FROM
            weather_forecastpivot
        WHERE
            hoursbefore IN (1, 6, 12, 24)
        GROUP BY
            api_name, month, hoursbefore;
    ''',
    "precipitationprobchart" : '''
        TRUNCATE weather_precipprobchart RESTART IDENTITY;

        WITH forecast_counts AS (
        SELECT 
            api_name, 
            hoursbefore, 
            FLOOR(forecasted_precip_prob / 10) * 10 AS forecast_prob_bucket, 
            COUNT(*) AS forecasted_count
        FROM weather_forecastpivot
        WHERE hoursbefore IN (1,6,12,24) AND forecasted_precip_prob IS NOT NULL
        GROUP BY api_name, FLOOR(forecasted_precip_prob / 10) * 10, hoursbefore
        ),
        actual_counts AS (
            SELECT 
                api_name, 
                hoursbefore, 
                FLOOR(forecasted_precip_prob / 10) * 10 AS forecast_prob_bucket, 
                COUNT(*) AS actual_count
            FROM weather_forecastpivot
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
            ROUND(COALESCE(actual_counts.actual_count::numeric / forecast_counts.forecasted_count::numeric * 100, 0), 2) AS actual_percentage,	
            forecast_counts.forecasted_count,
            COALESCE(actual_counts.actual_count, 0) AS actual_count,
            1 AS forecast_pivot_version
        FROM 
            forecast_counts
        LEFT JOIN 
            actual_counts
        ON 
            forecast_counts.api_name = actual_counts.api_name
            AND forecast_counts.hoursbefore = actual_counts.hoursbefore
            AND forecast_counts.forecast_prob_bucket = actual_counts.forecast_prob_bucket
        ORDER BY forecast_counts.api_name, forecast_counts.forecast_prob_bucket;''',
    "precipcalibrationchart": '''
        -- Compares average forecasted precipitation probability vs actual precipitation percentage
        WITH forecasted_percentages AS (
            SELECT
                api_name,
                hoursbefore,
                AVG(forecasted_precip_prob) AS avg_forecasted_prob
            FROM weather_forecastpivotv2
            WHERE forecasted_precip_prob IS NOT NULL
            GROUP BY
                api_name, hoursbefore
        ),
        total_count AS (
            SELECT
                api_name,
                hoursbefore,
                COUNT(*) AS total_count
            FROM weather_forecastpivotv2
            GROUP BY
                api_name, hoursbefore
        ),
        actual_count AS (
            SELECT
                api_name,
                hoursbefore,
                COUNT(*) AS actual_count
            FROM weather_forecastpivotv2
            WHERE current_precip_in > 0
            GROUP BY
                api_name, hoursbefore
        )

        SELECT 
            forecasted_percentages.api_name,
            forecasted_percentages.hoursbefore,
            ROUND(forecasted_percentages.avg_forecasted_prob, 2) AS avg_forecasted_prob,
            ROUND(COALESCE((actual_count.actual_count::numeric / total_count.total_count::numeric * 100), 0), 2) AS actual_percentage,
            total_count.total_count,
            COALESCE(actual_count.actual_count, 0) AS actual_count
        FROM 
            forecasted_percentages
        LEFT JOIN 
            total_count 
        ON 
            forecasted_percentages.api_name = total_count.api_name
            AND forecasted_percentages.hoursbefore = total_count.hoursbefore
        LEFT JOIN
            actual_count
        ON 
            forecasted_percentages.api_name = actual_count.api_name
            AND forecasted_percentages.hoursbefore = actual_count.hoursbefore
        ORDER BY
            forecasted_percentages.api_name,
            forecasted_percentages.hoursbefore;'''
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