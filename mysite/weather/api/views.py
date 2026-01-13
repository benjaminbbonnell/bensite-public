from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from ..models import HoursBeforeChart, MonthlyAverageChart
import calendar


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
    responses={
        200: OpenApiExample(
            "Successful Example of Hours Before Data",
            value=[
                {
                    "api_name": "openmeteo",
                    "hours_before": {
                        "0": 0.5,
                        "1": 1.2,
                        "24": 2.5,
                    },
                }
            ],
        )
    },
    tags=["Hours Before"],
)
class HBView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Hours Before"

    def get(self, request):

        rows = HoursBeforeChart.objects.values('api_name', 'hoursbefore', 'avg_dif')

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
    responses={
        200: OpenApiExample(
            "Successful Example of Monthly Average Data",
            value=[
                {
                    "api_name": "openmeteo",
                    "months": {
                        "January": {
                            "1": 0.51,
                            "6": 1.37,
                            "12": 1.62,
                            "24": 2.09,
                        },
                        "February": {
                            "1": 0.51,
                            "6": 1.37,
                            "12": 1.62,
                            "24": 2.09,
                        }
                    },
                }
            ],
        )
    },
    tags=["Monthly Averages"],
)
class MAView(APIView):
    authentication_classes =[]
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Monthly Averages"

    def get(self, request):
        rows = MonthlyAverageChart.objects.values('api_name', 'month', 'avg_dif', 'hoursbefore')

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

        for r in rows:
            response_dict = {}
            api_name = r["api_name"]
            month = r["month"]
            month_name = calendar.month_name[month]
            hoursbefore = r["hoursbefore"]
            avg_dif = r["avg_dif"]

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










