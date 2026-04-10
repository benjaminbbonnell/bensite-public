from django.urls import path
from . import views

app_name = 'typing_test'

urlpatterns = [
    path('', views.index, name='index'),
    path('get_new_string/', views.get_new_string, name='get_new_string'),
    path('redirect-to-bensite-index/', views.redirect_to_bensite_index, name='redirect_to_bensite_index'),
]