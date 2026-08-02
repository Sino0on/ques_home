from django.urls import path
from .views import *


urlpatterns = [
    path('', products_list, name='home'),
    path('product/<str:pk>', product_detail, name='product_detail'),
    path('update_data', update_data),
    path('sales-report/', sales_report, name='sales_report'),
    path('sales-report/export/', sales_report_export, name='sales_report_export'),
]
