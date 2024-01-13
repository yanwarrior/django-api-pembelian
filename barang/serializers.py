from rest_framework import serializers

from barang.models import Barang


class BarangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barang
        fields = ['id', 'nomor', 'nama',
                  'satuan', 'jenis', 'merek',
                  'tipe', 'ukuran', 'harga_beli',
                  'harga_jual', 'stok']
