from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_serializer
from drf_spectacular.types import OpenApiTypes
from ..models import HoursBeforeChart, MonthlyAverageChart, Locations, ForecastData, WeatherServices
import calendar
import math
import time
from decimal import Decimal
from datetime import datetime, timezone


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Successful Example of Hours Before Data",
            value=[
                {
                    "api_name": "openmeteo",
                    "hours_before": {
                        "0": 0,
                        "1": 0.89,
                        "2": 1.08,
                        "3": 1.22,
                        "4": 1.34,
                        "5": 1.44
                    },
                }
            ],
        )
    ]
)
class HoursBeforeResponseSerializer(serializers.Serializer):
    api_name = serializers.CharField()
    hours_before = serializers.DictField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Successful Example of Monthly Average Data",
            value=[
                {
                    "api_name": "openmeteo",
                    "months": {
                        "January": {
                            "1": 0.63,
                            "6": 1.49,
                            "12": 1.87,
                            "24": 2.24
                        },
                        "February": {
                            "1": 0.71,
                            "6": 1.76,
                            "12": 2.28,
                            "24": 3.08
                        }
                    },
                }
            ],
        )
    ]
)
class MonthlyAverageResponseSerializer(serializers.Serializer):
    api_name = serializers.CharField()
    months = serializers.DictField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Successful Example of Location Data",
            value=[
                {
                    "city_id": 1,
                    "city_name": "Washington",
                    "state_code": "DC",
                    "country_code": "USA",
                    "latitude": 38.9072,
                    "longitude": -77.0369
                },
                {
                    "city_id": 2,
                    "city_name": "Dallas",
                    "state_code": "TX",
                    "country_code": "USA",
                    "latitude": 32.7767,
                    "longitude": -96.797
                },
            ],
        )
    ]
)
class LocationResponseSerializer(serializers.Serializer):
    city_id = serializers.IntegerField()
    city_name = serializers.CharField()
    state_code = serializers.CharField()
    country_code = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Successful Example of Location Data",
            value=[
                {
                    "location": {
                        "location_id": 1,
                        "name": "Washington",
                        "state": "DC",
                        "country": "USA",
                        "latitude": 38.9072,
                        "longitude": -77.0369,
                        "gmt_time_epoch": 1771002000,
                        "gmt_time": "2026-02-13T17:00:00+00:00"
                    }
                },
                {
                    "1771002000": {
                        "visualcrossing": {
                            "temp_f": 35.0,
                            "feels_like_f": 27.8,
                            "precip_prob": 0.0,
                            "condition": "Clear"
                        },
                        "weathercom": {
                            "temp_f": 32.4,
                            "feels_like_f": 28.4,
                            "chance_of_rain": 0.0,
                            "chance_of_snow": 0.0,
                            "condition": "Sunny"
                        },
                    }
                }
            ],
        )
    ]
)
class CurrentForecastResponseSerializer(serializers.Serializer):
    city_id = serializers.IntegerField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    forecast_hours = serializers.IntegerField()


class HBView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Hours Before"

    @extend_schema(
        operation_id="get_hours_before",
        description="Retrieve weather forecast accuracy data grouped by API name and hours before forecast.",
        parameters=[
            OpenApiParameter(
                name="api_name",
                description="Filter results by API name(s). Use multiple times for multiple values: ?api_name=openmeteo&api_name=tomorrowio",
                required=False,
                type=OpenApiTypes.STR,
                style='form',
                explode=True,
                many=True,
                examples=[
                    OpenApiExample(name="All", value=""),
                    OpenApiExample(name="OpenMeteo only", value="openmeteo"),
                    OpenApiExample(name="OpenMeteo and TomorrowIO", value=["openmeteo", "tomorrowio"]),
                ],
            ),
            OpenApiParameter(
                name="hoursbefore",
                description="Filter results to forecasts with hours less than or equal to this value.",
                required=False,
                type=OpenApiTypes.INT,
                examples=[
                    OpenApiExample(name="All", value=""),
                    OpenApiExample(name="24 hours", value=24),
                    OpenApiExample(name="72 hours", value=72),
                ],
            ),
        ],
        responses=HoursBeforeResponseSerializer(many=True),
        tags=["Weather Analysis"],
    )
    def get(self, request):

        rows = HoursBeforeChart.objects.values("api_name", "hoursbefore", "avg_dif")

        hb_param = self.request.query_params.get("hoursbefore")
        if hb_param is not None:
            hb_param = int(hb_param)
            rows = rows.filter(hoursbefore__lte=hb_param)
        api_param = self.request.query_params.getlist("api_name")
        if api_param:
            rows = rows.filter(api_name__in=api_param)

        response_list = []

        for r in rows:
            response_dict = {}
            api_name = r["api_name"]
            hoursbefore = r["hoursbefore"]
            avg_dif = r["avg_dif"]

            if not any(d.get("api_name") == api_name for d in response_list):
                response_dict["api_name"] = api_name
                response_dict["hours_before"] = {}
                response_list.append(response_dict)
            for response in response_list:
                if response["api_name"] == api_name:
                    response["hours_before"][hoursbefore] = avg_dif

        return Response(response_list)

class MAView(APIView):
    authentication_classes =[]
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Monthly Averages"

    @extend_schema(
        operation_id="get_monthly_average",
        description="Retrieve weather forecast accuracy data grouped by API name, month, and hours before forecast.",
        parameters=[
            OpenApiParameter(
                name="api_name",
                description="Filter results by API name(s). Use multiple times for multiple values: ?api_name=openmeteo&api_name=tomorrowio",
                required=False,
                type=OpenApiTypes.STR,
                style='form',
                explode=True,
                many=True,
                examples=[
                    OpenApiExample(name="All", value=""),
                    OpenApiExample(name="OpenMeteo only", value="openmeteo"),
                    OpenApiExample(name="OpenMeteo and TomorrowIO", value=["openmeteo", "tomorrowio"]),
                ],
            ),
            OpenApiParameter(
                name="hoursbefore",
                description="Filter results to forecasts with hours less than or equal to this value.",
                required=False,
                type=OpenApiTypes.INT,
                examples=[
                    OpenApiExample(name="All", value=""),
                    OpenApiExample(name="1 hour", value=1),
                    OpenApiExample(name="12 hours", value=12),
                ],
            ),
            OpenApiParameter(
                name="month",
                description="Filter results by month integer. Use multiple times for multiple values: ?month=1&month=4",
                required=False,
                type=OpenApiTypes.STR,
                style='form',
                explode=True,
                many=True,
                examples=[
                    OpenApiExample(name="All", value=""),
                    OpenApiExample(name="November", value="11"),
                    OpenApiExample(name="December", value="12"),
                ],
            ),
        ],
        responses=MonthlyAverageResponseSerializer(many=True),
        tags=["Weather Analysis"],
    )
    def get(self, request):
        rows = MonthlyAverageChart.objects.values("api_name", "month", "avg_dif", "hoursbefore")

        # hours before must be an integer
        hb_param = self.request.query_params.get("hoursbefore")
        if hb_param is not None:
            try:
                hb_param = int(hb_param)
                if hb_param < 0:
                    return Response(
                        {"error": "hoursbefore must be a positive integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                rows = rows.filter(hoursbefore__lte=hb_param)
            except ValueError:
                return Response(
                    {"error": "Invalid hoursbefore parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        #month must be an integer between 1 and 12
        mon_param = self.request.query_params.getlist("month")
        if mon_param:
            try:
                mon_param = [int(m) for m in mon_param if m]
                if any(m < 1 or m > 12 for m in mon_param):
                    return Response(
                        {"error": "month must be between 1 and 12"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if mon_param:
                    rows = rows.filter(month__in=mon_param)
            except ValueError:
                return Response(
                    {"error": "Invalid month parameter. Must be integers between 1-12."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        api_param = self.request.query_params.getlist("api_name")
        if api_param:
            rows = rows.filter(api_name__in=api_param)

        response_list = []

        for row in rows:
            response_dict = {}
            api_name = row["api_name"]
            month = row["month"]
            month_name = calendar.month_name[month]
            hoursbefore = row["hoursbefore"]
            avg_dif = row["avg_dif"]

            if not any(d.get("api_name") == api_name for d in response_list):
                response_dict["api_name"] = api_name
                response_dict["months"] = {}
                response_list.append(response_dict)
            for response in response_list:
                if response["api_name"] == api_name:
                    if month_name not in response["months"]:
                        response["months"][month_name] = {}
                    response["months"][month_name][hoursbefore] = avg_dif

        return Response(response_list)

class LocationList(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Location List"

    @extend_schema(
        operation_id="get_location_list",
        description="Retrieve a list of locations with their ID, name, state, country, latitude, and longitude.",
        responses=LocationResponseSerializer(many=True),
        tags=["Forecasts"],
    )
    def get(self, request):
        rows = Locations.objects.values("city_id", "city_name", "state_code", "country_code", "latitude", "longitude").order_by("city_id")

        response_list = []

        for r in rows:
            response_dict = {
                "city_id": r["city_id"],
                "city_name": r["city_name"],
                "state_code": r["state_code"],
                "country_code": r["country_code"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
            }
            response_list.append(response_dict)

        return Response(response_list)
    
class CurrentForecast(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Current Forecast"
    
    @extend_schema(
        operation_id="get_current_forecast",
        description="Retrieve a forecast for each weather API. Defaults to only current forecast but can extend to 12 hours.",
        responses=CurrentForecastResponseSerializer(many=True),
        tags=["Forecasts"],
        parameters=[
                OpenApiParameter(
                    name="city_id",
                    description="Filter results by city ID. Can be retrieved from the location list API. If this is left blank latitude and longitude must be specified.",
                    required=False,
                    type=OpenApiTypes.INT,
                    examples=[
                        OpenApiExample(name="Washington DC", value=1),
                        OpenApiExample(name="Dallas", value=2),
                    ],
                ),
                OpenApiParameter(
                    name="lat",
                    description="Latitude coordinate. Must be used with lon parameter. Will find nearest city by Haversine distance if city_id is not specified.",
                    required=False,
                    type=OpenApiTypes.NUMBER,
                    examples=[
                        OpenApiExample(name="Washington DC", value=38.9072),
                        OpenApiExample(name="Dallas", value=32.7767),
                    ],
                ),
                OpenApiParameter(
                    name="lon",
                    description="Longitude coordinate. Must be used with lat parameter. Will find nearest city by Haversine distance if city_id is not specified.",
                    required=False,
                    type=OpenApiTypes.NUMBER,
                    examples=[
                        OpenApiExample(name="Washington DC", value=-77.0369),
                        OpenApiExample(name="Dallas", value=-96.797),
                    ],
                ),
                OpenApiParameter(
                    name="forecast_hours",
                    description="Number of hours ahead to get forecasts for (0-12). Defaults to 0 (current forecast only).",
                    required=False,
                    type=OpenApiTypes.INT,
                    examples=[
                        OpenApiExample(name="Current only", value=0),
                        OpenApiExample(name="6 hours", value=6),
                        OpenApiExample(name="12 hours", value=12),
                    ],
                ),
            ],
    )
    def get(self, request):

        rows = ForecastData.objects.all()
        current_time = round((int(time.time())) // 3600) * 3600 #current time in unix epoch time rounded down to the nearest hour to match the forecast data

        city_id_param = self.request.query_params.get("city_id") #city ID can be retrieved from the location list API
        lat_param = self.request.query_params.get("lat")
        lon_param = self.request.query_params.get("lon")
        forecast_hours_param = self.request.query_params.get("forecast_hours")


        if forecast_hours_param is not None:
            try:
                forecast_hours_param = int(forecast_hours_param)
                if forecast_hours_param < 0 or forecast_hours_param > 12:
                    return Response(
                        {"error": "forecast_hours must be an integer between 0 and 12."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"error": "forecast_hours must be an integer between 0 and 12."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            forecast_hours_param = 0

        filter_time = current_time + (forecast_hours_param * 3600)
    

        # If a city ID is specified, filter to that city. If not, calculate the closest distance to the specified coordinates. If neither is specified, return a bad request.
        if city_id_param:
            try:
                city_id_param_converted = int(city_id_param)
            except ValueError:
                return Response(
                    {"error": "Invalid city ID specified"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            city_id_param = city_id_param_converted
            if not Locations.objects.filter(pk=city_id_param).exists():
                return Response(
                    {"error": "Invalid city ID specified"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif lat_param and lon_param:
            lat_param_converted = math.radians(Decimal(lat_param))
            lon_param_converted = math.radians(Decimal(lon_param))
            try:
                locations = Locations.objects.all()
                min_distance = float("inf")
                min_location = None

                #there's definitely a library out there for this but it's more fun to do it manually
                for location in locations:
                    location_lat = math.radians(location.latitude)
                    location_lon = math.radians(location.longitude)

                    haversine_a = (math.sin((location_lat - lat_param_converted)/2) ** 2) + ((math.sin((location_lon - lon_param_converted)/2) ** 2) * math.cos(lat_param_converted) * math.cos(location_lat))

                    distance = 2 * math.asin(math.sqrt(haversine_a)) * 6371.009 #mean radius of the earth

                    if distance < min_distance:
                        min_distance = distance
                        min_location = location.city_id
                    
                    if min_distance == 0:
                        break
                
                city_id_param = min_location
            except ValueError:
                return Response(
                    {"error": "Invalid coordinates specified."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                    {"error": "City ID or latitude and longitude must be specified"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        


        rows = rows.filter(city_id=city_id_param).filter(forecast_epoch__lte=filter_time).filter(forecast_made=current_time)

        location = Locations.objects.get(pk=city_id_param)

        response_list = []

        location_dict = {}
        location_dict["location"] = {
            "location_id": location.city_id,
            "name": location.city_name,
            "state": location.state_code,
            "country": location.country_code,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "gmt_time_epoch": current_time,
            "gmt_time": datetime.fromtimestamp(current_time, tz=timezone.utc).isoformat()
        }

        response_list.append(location_dict)

        forecasts_dict = {}

        for row in rows:
            data = {
            "temp_f": row.temp_f,
            "feels_like_f": row.feelslike_f,
            "chance_of_rain": row.chance_of_rain,
            "chance_of_snow": row.chance_of_snow,
            "precip_prob": row.precip_prob,

            "condition": row.condition,
            }
            
            if row.forecast_epoch not in forecasts_dict:
                forecasts_dict[row.forecast_epoch] = {}
            
            forecasts_dict[row.forecast_epoch][row.api_name] = {k: v for k, v in data.items() if v is not None}
        
        response_list.append(forecasts_dict)
        return Response(response_list)