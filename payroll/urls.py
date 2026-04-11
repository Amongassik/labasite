from django.urls import path
from . import views

urlpatterns = [
    path('',views.employee_list,name='index'),
    path('add/',views.employee_add,name='add'),
    path('delete/<int:pk>/',views.employee_delete,name='delete'),
    path('report/',views.print_salary_report,name='report')
]