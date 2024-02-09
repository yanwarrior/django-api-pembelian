from django.urls import path

from supplier.views import supplier_list, supplier_detail, supplier_choice

app_name = "supplier"

urlpatterns = [
    path('', supplier_list, name='supplier-list'),
    path('<int:id>/', supplier_detail, name='supplier-detail'),
    path('<str:nomor>/choice/', supplier_choice, name='supplier-choice'),
]