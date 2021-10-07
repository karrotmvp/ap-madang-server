from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation),
    path('region', views.region),
]