from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/new/', views.client_create, name='client_create'),
    path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    path('clients/search/ajax/',views.client_search_ajax,name='client_search_ajax'),
    path('products/', views.products_list, name='products_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    path('orders/new/', views.order_create, name='order_create'),
    path('report/clients-orders/', views.clients_orders_report, name='clients_orders_report'),
    path('report/orders-clients',views.orders_report,name='order_report')
]