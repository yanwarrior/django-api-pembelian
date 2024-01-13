from rest_framework import serializers

from pembelian.models import Pembelian


class PembelianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pembelian
        fields = ['id', 'nomor', 'tanggal',
                  'supplier', 'is_published',]
        read_only_fields = ['is_published']