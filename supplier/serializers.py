from rest_framework import serializers

from supplier.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'nama', 'alamat',
                  'telepon', 'bank', 'rekening',
                  'pic']