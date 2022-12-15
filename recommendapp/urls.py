from django.urls import path, include
from recommendapp import views

urlpatterns = [
    path('',views.index),
    path('/refresh',views.refresh,name="refresh")
]