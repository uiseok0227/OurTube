from django.urls import path, include
from dashboardapp import views

urlpatterns = [
    path('',views.index),
    path('<int:category_id>/', views.detail),
    path('logout/',views.logout,name='logout')
]