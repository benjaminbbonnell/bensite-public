from django.shortcuts import render, redirect
from .models import HoursBeforeChart, WeatherServices, SiteStats, MonthlyAverageChart, PrecipProbChart
from decimal import Decimal
from num2words import num2words
import calendar

# Create your views here.

def index(request):

    tfc_obj = SiteStats.objects.get(name="total_forecast_count")
    total_forecast_count = "{:,}".format(int(tfc_obj.stat))

    api_count = SiteStats.objects.get(name="total_api_count").stat
    api_count_formatted = num2words(api_count, lang='en')

    location_count = int(SiteStats.objects.get(name="total_location_count").stat)


    hbc_data = HoursBeforeChart.objects.values('api_name', 'avg_dif', 'hoursbefore', 'signed_dif', 'forecast_pivot_version').order_by('hoursbefore', 'api_name')
    ma_data = MonthlyAverageChart.objects.values('api_name', 'month', 'avg_dif', 'hoursbefore', 'forecast_pivot_version').order_by('api_name', 'month', 'hoursbefore')
    pprob_data = PrecipProbChart.objects.values('api_name', 'hoursbefore', 'forecast_prob_bucket', 'actual_percentage', 'forecast_pivot_version')
    api_names = WeatherServices.objects.values_list('api_ref_name', 'api_display_name')
    api_name_dict = {item[0]: item[1] for item in api_names}

    def hbc_series_helper(chart_data, abs_mode, version=1):
        chart_data = chart_data.filter(forecast_pivot_version=version)
        hbc_series_data = {}
        for item in chart_data:
            if item['api_name'] not in hbc_series_data:
                hbc_series_data[item['api_name']] = []
            if abs_mode:
                avg_dif = float(item['avg_dif']) if isinstance(item['avg_dif'], Decimal) else item['avg_dif']
            else:
                avg_dif = float(item['signed_dif']) if isinstance(item['signed_dif'], Decimal) else item['signed_dif']
            if item['hoursbefore'] < 180:
                hbc_series_data[item['api_name']].append([item['hoursbefore'], avg_dif])
        return [{'name': api_name_dict.get(api_name), 'data': hbc_series_data[api_name]} for api_name in hbc_series_data]

    hbc_categories = sorted(set(item['hoursbefore'] for item in hbc_data))
    hbc_series_abs_v1 = hbc_series_helper(hbc_data, True)
    hbc_series_signed_v1 = hbc_series_helper(hbc_data, False)
    hbc_series_abs_v2 = hbc_series_helper(hbc_data, True, version=2)
    hbc_series_signed_v2 = hbc_series_helper(hbc_data, False, version=2)

    def precip_prob_helper(chart_data, hoursbefore, version=1):
        chart_data = chart_data.filter(forecast_pivot_version=version)
        precip_prob_series_data = {}
        for item in chart_data:
            if item['hoursbefore'] == hoursbefore:
                if item['api_name'] not in precip_prob_series_data:
                    precip_prob_series_data[item['api_name']] = []
                precip_prob_series_data[item['api_name']].append([float(item['forecast_prob_bucket']), float(item['actual_percentage'])])
        
        for api_name in precip_prob_series_data:
            precip_prob_series_data[api_name].sort(key=lambda point: point[0])
        
        return [{'name': api_name_dict.get(api_name), 'data': precip_prob_series_data[api_name]} for api_name in precip_prob_series_data]

    pprob_categories = sorted(set(float(item['forecast_prob_bucket']) for item in pprob_data))
    pprob_series_v1_1h = precip_prob_helper(pprob_data, 1)
    pprob_series_v1_6h = precip_prob_helper(pprob_data, 6)
    pprob_series_v1_12h = precip_prob_helper(pprob_data, 12)
    pprob_series_v1_24h = precip_prob_helper(pprob_data, 24)
    pprob_series_v2_1h = precip_prob_helper(pprob_data, 1, version=2)
    pprob_series_v2_6h = precip_prob_helper(pprob_data, 6, version=2)
    pprob_series_v2_12h = precip_prob_helper(pprob_data, 12, version=2)
    pprob_series_v2_24h = precip_prob_helper(pprob_data, 24, version=2)

    def convert_ma_format(month, hoursbefore):
        return f"{calendar.month_name[month]} - {hoursbefore} hours before"

    def ma_series_helper(chart_data, version=1):
        chart_data = chart_data.filter(forecast_pivot_version=version)
        ma_series_data = {}
        for item in chart_data:
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

        return ma_series

    ma_cat_data = sorted({
        (item['month'], item['hoursbefore'])
        for item in ma_data

    })

    ma_categories = [convert_ma_format(item[0], item[1]) for item in ma_cat_data]
    ma_series_v1 = ma_series_helper(ma_data, version=1)
    ma_series_v2 = ma_series_helper(ma_data, version=2)

    context = {
        'hbc_categories': hbc_categories,
        'hbc_series_abs_v1': hbc_series_abs_v1,
        'hbc_series_signed_v1': hbc_series_signed_v1,
        'hbc_series_abs_v2': hbc_series_abs_v2,
        'hbc_series_signed_v2': hbc_series_signed_v2,
        'ma_categories' : ma_categories,
        'ma_series_v1' : ma_series_v1,
        'ma_series_v2' : ma_series_v2,
        'pprob_categories' : pprob_categories,
        'pprob_series_v1_1h' : pprob_series_v1_1h,
        'pprob_series_v1_6h' : pprob_series_v1_6h,
        'pprob_series_v1_12h' : pprob_series_v1_12h,
        'pprob_series_v1_24h' : pprob_series_v1_24h,
        'pprob_series_v2_1h' : pprob_series_v2_1h,
        'pprob_series_v2_6h' : pprob_series_v2_6h,
        'pprob_series_v2_12h' : pprob_series_v2_12h,
        'pprob_series_v2_24h' : pprob_series_v2_24h,
        'forecastcount': total_forecast_count,
        'api_count': api_count_formatted,
        'location_count': location_count
    }
    return render(request, 'weather/weather.html', context)


def redirect_to_bensite_index(request):
    return redirect('bensite:index')  # Redirect to the 'index' view in the 'bensite' apps


















