from rest_framework import serializers

from supplier.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'nomor',
            'nama',
            'alamat',
            'telepon',
            'contact_person',
            'bank',
            'rekening',
        ]