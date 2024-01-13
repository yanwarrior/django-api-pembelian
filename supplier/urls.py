from django.urls import path

from supplier.views import supplier_list, supplier_detail

app_name = "supplier"

urlpatterns = [
    path('', supplier_list, name='supplier-list'),
    path('<int:pk>/', supplier_detail, name='supplier-detail'),
]