from django.urls import path
from . import views

urlpatterns=[
    path('',views.dashboard,name='dashboard'),
    path('clear/',views.data_clear,name='clear_data'),
    path('filter/',views.filter_data,name='filter_data'),
    path('clear-filter/', views.clear_filter, name='clear_filter'),
]