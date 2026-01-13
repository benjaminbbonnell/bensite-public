from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
from .api import HBView, MAView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

app_name = 'weather'

urlpatterns = [
    path('', views.index, name='index'),
    path('redirect-to-bensite-index/', views.redirect_to_bensite_index, name='redirect_to_bensite_index'),
    path('api/hb/', HBView.as_view(), name='Hours Before'),
    path('api/ma/', MAView.as_view(), name='Monthly Average'),
    path('api/schema/', csrf_exempt(SpectacularAPIView.as_view()), name='schema'),
    # Optional UI:
    path('api/', csrf_exempt(SpectacularSwaggerView.as_view(url_name='weather:schema')), name='swagger-ui'),
    path('api/redoc/', csrf_exempt(SpectacularRedocView.as_view(url_name='weather:schema')), name='redoc'),
]