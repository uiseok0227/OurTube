from django.urls import path, include
from profileapp import views

urlpatterns = [
    path('',views.index),
]