from rest_framework import serializers

from pembelian.models import Pembelian, Pembayaran, Item


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


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'barang', 'pembelian',
                  'diskon', 'harga_supplier', 'jumlah',
                  'subtotal', 'keterangan']
        read_only_fields = ['subtotal',]