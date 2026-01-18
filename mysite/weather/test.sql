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