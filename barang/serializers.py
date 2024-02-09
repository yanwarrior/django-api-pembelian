from rest_framework import serializers

from barang.models import Barang


class BarangSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if attrs['harga_jual'] <= attrs['harga_beli']:
            raise serializers.ValidationError('Harga jual must be greater than harga beli')

        return attrs

    class Meta:
        model = Barang
        fields = [
            'id',
            'nomor',
            'nama',
            'jenis',
            'satuan',
            'harga_beli',
            'harga_jual',
            'stok',
        ]
