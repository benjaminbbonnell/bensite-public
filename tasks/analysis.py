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
        TRUNCATE weather_hoursbeforechart RESTART IDENTITY;

        INSERT INTO weather_hoursbeforechart(api_name, avg_dif, hoursbefore)
        SELECT api_name, ROUND(AVG(ABS(currenttemp - temp_f)), 2) AS avg_dif, hoursbefore
        FROM weather_forecastpivot
        GROUP BY api_name, hoursbefore
        ORDER BY hoursbefore, api_name;
    ''',
    "monthlyaveragechart": '''
        TRUNCATE weather_monthlyaveragechart RESTART IDENTITY;

        INSERT INTO weather_monthlyaveragechart(api_name, month, avg_dif, hoursbefore)
        SELECT
            api_name,
            to_char(to_timestamp(forecast_made), 'MM')::int as month,
            ROUND(AVG(ABS(currenttemp - temp_f)), 2) AS avg_dif,
            hoursbefore
        FROM
            weather_forecastpivot
        WHERE
            hoursbefore IN (1, 6, 12, 24)
        GROUP BY
            api_name, month, hoursbefore;
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
        print("qauery complete.")

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