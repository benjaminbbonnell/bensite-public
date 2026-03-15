from django.urls import path
from . import views

app_name = 'typing_test'

urlpatterns = [
    path('', views.index, name='index'),
    path('redirect-to-bensite-index/', views.redirect_to_bensite_index, name='redirect_to_bensite_index'),
]