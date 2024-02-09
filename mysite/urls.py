from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin', admin.site.urls),
    path('user/signin/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('barang/', include('barang.urls', namespace='barang')),
    path('supplier/', include('supplier.urls', namespace='supplier')),
    path('pembelian/', include('pembelian.urls', namespace='pembelian')),
    path('stok/', include('stok.urls', namespace='stok')),
]
