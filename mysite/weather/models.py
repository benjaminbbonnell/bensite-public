from django.db import models

# Create your models here.


class ForecastData(models.Model):
    api_name = models.CharField(max_length=100)
    city_id = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=100)
    forecast_made = models.BigIntegerField()
    forecast_epoch = models.BigIntegerField()
    temp_f = models.DecimalField(max_digits=5, decimal_places=2)
    feelslike_f = models.DecimalField(max_digits=5, decimal_places=2)
    condition = models.CharField(max_length=100, null=True)
    precip_prob = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    chance_of_rain = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    chance_of_snow = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    precip_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    precip_type = models.CharField(max_length=100, null=True)
    snow_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    rain_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    sleet_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    will_it_rain = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        verbose_name_plural = "Forecast Data"

class WeatherServices(models.Model):
    api_ref_name = models.CharField(max_length=100)
    api_display_name = models.CharField(max_length=100)
    days = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    hourly_api_limit = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Weather Services"

class Locations(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=2)
    country_code = models.CharField(max_length=3)
    latitude = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    longitude = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    accuweathercode = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Locations"

class ForecastPivot(models.Model):
    api_name = models.CharField(max_length=100)
    city_id = models.IntegerField(blank=True, null=True)
    city_name = models.CharField(max_length=100)
    forecast_made = models.IntegerField(null=True)
    forecast_epoch = models.IntegerField(null=True)
    currenttemp = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    temp_f = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    hoursbefore = models.IntegerField(null=True)
    forecasted_precip_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    forecasted_precip_prob = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    current_precip_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    current_precip_prob = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        verbose_name_plural = "Forecast Pivot"

class ForecastPivotV2(models.Model):
    api_name = models.CharField(max_length=100)
    city_id = models.IntegerField(blank=True, null=True)
    city_name = models.CharField(max_length=100)
    forecast_made = models.IntegerField(null=True)
    forecast_epoch = models.IntegerField(null=True)
    currenttemp = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    temp_f = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    hoursbefore = models.IntegerField(null=True)
    forecasted_precip_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    forecasted_precip_prob = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    current_precip_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    current_precip_prob = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        verbose_name_plural = "Forecast Pivot v2"

class HistoricalData(models.Model):
    city_id = models.IntegerField(blank=True, null=True)
    city_name = models.CharField(max_length=100)
    api_name = models.CharField(max_length=100)
    time_epoch = models.IntegerField(null=True)
    temp_f = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    precip_in = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    precip_prob = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        verbose_name_plural = "Historical Data"

class HoursBeforeChart(models.Model):
    api_name = models.CharField(max_length=100)
    avg_dif = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    signed_dif = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    hoursbefore = models.IntegerField(null=True)
    forecast_pivot_version = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Hours Before Chart"

class MonthlyAverageChart(models.Model):
    api_name = models.CharField(max_length=100)
    month = models.IntegerField(null=True)
    avg_dif = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    hoursbefore = models.IntegerField(null=True)
    forecast_pivot_version = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Monthly Average Chart"

class PrecipProbChart(models.Model):
    api_name = models.CharField(max_length=100)
    hoursbefore = models.IntegerField(null=True)
    forecast_prob_bucket = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    actual_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    forecasted_count = models.IntegerField(null=True)
    actual_count = models.IntegerField(null=True)
    forecast_pivot_version = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Precipitation Probability Chart"

class CalibrationChart(models.Model):
    api_name = models.CharField(max_length=100)
    hoursbefore = models.IntegerField(null=True)
    calibration_stat = models.IntegerField(null=True)
    forecast_pivot_version = models.IntegerField(null=True)


class SiteStats(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    stat = models.DecimalField(max_digits=100, decimal_places=2, null=True)

    class Meta:
        verbose_name_plural = "Site Stats"



















