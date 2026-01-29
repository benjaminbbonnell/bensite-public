from django.shortcuts import render, redirect
from .models import HoursBeforeChart, WeatherServices, SiteStats, MonthlyAverageChart
from decimal import Decimal
import calendar

# Create your views here.

def index(request):

    tfc_obj = SiteStats.objects.get(name="total_forecast_count")
    total_forecast_count = "{:,}".format(int(tfc_obj.stat))

    hbc_data = HoursBeforeChart.objects.values('api_name', 'avg_dif', 'hoursbefore', 'signed_dif').order_by('hoursbefore', 'api_name')
    ma_data = MonthlyAverageChart.objects.values('api_name', 'month', 'avg_dif', 'hoursbefore').order_by('api_name', 'month', 'hoursbefore')
    api_names = WeatherServices.objects.values_list('api_ref_name', 'api_display_name')
    api_name_dict = {item[0]: item[1] for item in api_names}

    #hour before chart, series is a , categories are api_name
    hbc_series_data_abs = {}
    for item in hbc_data:
        if item['api_name'] not in hbc_series_data_abs:
            hbc_series_data_abs[item['api_name']] = []
        avg_dif = float(item['avg_dif']) if isinstance(item['avg_dif'], Decimal) else item['avg_dif']
        if item['hoursbefore'] < 180:
            hbc_series_data_abs[item['api_name']].append([item['hoursbefore'], avg_dif])

    hbc_series_data_signed = {}
    for item in hbc_data:
        if item['api_name'] not in hbc_series_data_signed:
            hbc_series_data_signed[item['api_name']] = []
        avg_dif = float(item['signed_dif']) if isinstance(item['signed_dif'], Decimal) else item['signed_dif']
        if item['hoursbefore'] < 180:
            hbc_series_data_signed[item['api_name']].append([item['hoursbefore'], avg_dif])

    hbc_categories = sorted(set(item['hoursbefore'] for item in hbc_data))
    hbc_series_abs = [{'name': api_name_dict.get(api_name), 'data': hbc_series_data_abs[api_name]} for api_name in hbc_series_data_abs]
    hbc_series_signed = [{'name': api_name_dict.get(api_name), 'data': hbc_series_data_signed[api_name]} for api_name in hbc_series_data_signed]

    #monthly average chart

    def convert_ma_format(month, hoursbefore):
        return f"{calendar.month_name[month]} - {hoursbefore} hours before"


    ma_cat_data = sorted({
        (item['month'], item['hoursbefore'])
        for item in ma_data

    })

    ma_categories = [convert_ma_format(item[0], item[1]) for item in ma_cat_data]


    ma_series_data = {}
    for item in ma_data:
        if item['api_name'] not in ma_series_data:
            ma_series_data[item['api_name']] = []
        avg_dif = float(item['avg_dif']) if isinstance(item['avg_dif'], Decimal) else item['avg_dif']
        ma_series_data[item['api_name']].append((convert_ma_format(item['month'], item['hoursbefore']), avg_dif))

    ma_series = [
        {
            'name': api_name_dict.get(api_name),
            'data': [{'x': ma_categories.index(category), 'y': avg_dif} for category, avg_dif in data]
        }
        for api_name, data in ma_series_data.items()
    ]


    context = {
        'hbc_series_abs': hbc_series_abs,
        'hbc_series_signed': hbc_series_signed,
        'hbc_categories': hbc_categories,
        'ma_categories' : ma_categories,
        'ma_series' : ma_series,
        'forecastcount': total_forecast_count
    }
    return render(request, 'weather/weather.html', context)


def redirect_to_bensite_index(request):
    return redirect('bensite:index')  # Redirect to the 'index' view in the 'bensite' apps


















