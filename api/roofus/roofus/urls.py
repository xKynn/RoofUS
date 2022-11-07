from django.contrib import admin

from django.urls import include, path

from rest_framework import routers

from roofus_api import views

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('predict', views.PredictionAPIView.as_view())
]