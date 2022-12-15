from django.urls import path, include
from friendapp import views

urlpatterns = [
    path('',views.index),
    path('search/',views.search,name="search"),
    path('friend/',views.add_friend,name="friend"),
    path('friendinfo/',views.friendInfo,name="friendinfo"),
    path('delete/',views.delete ,name = "delete"),
    path('interestinfo/',views.interestInfo,name="interestinfo")
]