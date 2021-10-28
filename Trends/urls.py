from django.urls import path,include
from . import views
from django.conf.urls import url


urlpatterns = [
    path('',views.index),
    url('interest',views.interest_over_time,name='interest')
]