from django.urls import path
from . import views

urlpatterns =[
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('create/', views.employee_create, name='employee_create'),
    path('update/<int:pk>/', views.employee_update, name='employee_update'),
    path('delete/<int:pk>/', views.employee_delete, name='employee_delete'),
]