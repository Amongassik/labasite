from django.urls import path
from . import views

app_name = 'data_exchange'

urlpatterns=[
    path('',views.index,name ='index'),
    path('clear-data/',views.clear_data,name='clear_data')
]