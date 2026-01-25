WITH total AS
(SELECT api_name, COUNT(*) AS total_count
FROM weather_forecastpivot
GROUP BY api_name
),
good AS
(SELECT api_name, COUNT(*) AS good_count
FROM weather_forecastpivot
WHERE ABS(temp_f - currenttemp) < 5
GROUP BY api_name)


SELECT total.api_name, total.total_count, good.good_count, good.good_count::float / total.total_count AS percent_good
FROM total
LEFT JOIN good ON total.api_name = good.api_name;

WITH all_rows AS
(
    SELECT api_name, temp_diff,
    CASE
        WHEN temp_diff <= 1 THEN '1'
        WHEN temp_diff <= 2 THEN '2'
        WHEN temp_diff <= 3 THEN '3'
        WHEN temp_diff <= 4 THEN '4'
        WHEN temp_diff <= 5 THEN '5'
        WHEN temp_diff <= 10 THEN '10'
        ELSE '10+'
    END AS diff_category
    FROM 
    (
        SELECT api_name, ABS(temp_f - currenttemp) AS temp_diff
        FROM weather_forecastpivot
    ) AS t
)
total_rows AS


SELECT api_name, diff_category, count(diff_category)
FROM all_rows
GROUP BY api_name, diff_category;




WITH current AS (
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
        'ensemble' AS api_name,
        forecast_data.city AS city_name,
	    forecast_data.city_id,
        forecast_made,
        forecast_epoch,
        ROUND(AVG(currenttemps.currenttemp), 2),
        ROUND(avg(forecast_data.temp_f), 2),
        forecast_data.hoursbefore
        FROM forecast_data
        JOIN currenttemps ON forecast_data.city_id = currenttemps.city_id AND forecast_data.api_name = currenttemps.api_name
        WHERE forecast_data.forecast_epoch = (SELECT current FROM current) AND hoursbefore < 72
        GROUP BY forecast_data.city, forecast_data.city_id, forecast_made, forecast_epoch, forecast_data.hoursbefore;