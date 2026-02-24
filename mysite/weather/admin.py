from django.contrib import admin


from .models import ForecastData, WeatherServices, Locations, SiteStats

class fd(admin.ModelAdmin):
    list_display = ('api_name', 'city', 'forecast_made', 'forecast_epoch', 'temp_f', 'will_it_rain', 'chance_of_rain')

class ws(admin.ModelAdmin):
    list_display = ('api_ref_name', 'api_display_name', 'days', 'hourly_api_limit')

class loc(admin.ModelAdmin):
    list_display = ('city_id', 'city_name', 'state_code', 'country_code', 'latitude', 'longitude', 'accuweathercode')

class ss(admin.ModelAdmin):
    list_display = ('name', 'stat')

admin.site.register(ForecastData, fd)
admin.site.register(WeatherServices, ws)
admin.site.register(Locations, loc)
admin.site.register(SiteStats, ss)
