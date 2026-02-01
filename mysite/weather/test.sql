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






WITH observations AS (
    SELECT 
        city,
        forecast_epoch,
        precip_in AS actual_precip,
        CASE 
            WHEN precip_in > 0 THEN 1 
            ELSE 0 
        END AS it_rained
    FROM weather_forecastdata
    WHERE forecast_epoch = forecast_made 
        AND api_name = 'openmeteo'
),
forecasts_with_obs AS (
    SELECT 
        f.city,
        f.forecast_epoch,
        f.precip_prob,
        f.precip_in AS forecasted_precip,
        FLOOR(EXTRACT(EPOCH FROM (to_timestamp(f.forecast_epoch) - to_timestamp(f.forecast_made)))/3600) AS hours_before,
        o.actual_precip,
        o.it_rained,
        CASE
            WHEN f.precip_prob < 10 THEN '0-10%'
            WHEN f.precip_prob < 20 THEN '10-20%'
            WHEN f.precip_prob < 30 THEN '20-30%'
            WHEN f.precip_prob < 50 THEN '30-50%'
            WHEN f.precip_prob < 70 THEN '50-70%'
            ELSE '70%+'
        END AS prob_bucket
    FROM weather_forecastdata f
    INNER JOIN observations o 
        ON f.city = o.city 
        AND f.forecast_epoch = o.forecast_epoch
    WHERE f.api_name = 'openmeteo'
        AND f.forecast_epoch > f.forecast_made
)
SELECT 
    hours_before,
    prob_bucket,
    COUNT(*) AS total_forecasts,
    SUM(it_rained) AS actual_rain_count,
    ROUND(100.0 * SUM(it_rained) / COUNT(*), 2) AS actual_rain_percent,
    ROUND(AVG(precip_prob), 2) AS avg_predicted_prob,
    ROUND(100.0 * SUM(it_rained) / COUNT(*) - AVG(precip_prob), 2) AS wet_bias_percent,
    ROUND(AVG(actual_precip), 2) AS avg_actual_precip_in
FROM forecasts_with_obs
GROUP BY hours_before, prob_bucket
ORDER BY hours_before DESC,
    CASE WHEN prob_bucket = '0-10%' THEN 1
         WHEN prob_bucket = '10-20%' THEN 2
         WHEN prob_bucket = '20-30%' THEN 3
         WHEN prob_bucket = '30-50%' THEN 4
         WHEN prob_bucket = '50-70%' THEN 5
         ELSE 6
    END;