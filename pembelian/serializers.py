from rest_framework import serializers

from pembelian.models import Pembelian, Pembayaran


class PembelianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pembelian
        fields = ['id', 'nomor', 'tanggal',
                  'supplier', 'is_published',]
        read_only_fields = ['is_published']


class PembayaranSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pembayaran
        fields = ['id', 'nomor', 'pembelian',
                  'metode', 'diskon', 'ppn',
                  'total', 'is_paid', 'dibayar',
                  'kembali', 'sisa',]
        read_only_fields = ['nomor', 'pembelian', 'metode',
                            'total', 'is_paid', 'kembali',
                            'sisa']