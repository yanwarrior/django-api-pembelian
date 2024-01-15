from rest_framework import serializers

from pembelian.models import Pembelian, Pembayaran, Item, Hutang


class PembayaranSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pembayaran
        fields = ['id', 'nomor', 'pembelian',
                  'metode', 'diskon', 'ppn',
                  'total', 'is_paid', 'dibayar',
                  'kembali', 'sisa', 'tempo',
                  'tanggal_jatuh_tempo']
        read_only_fields = ['nomor', 'pembelian', 'metode',
                            'total', 'is_paid', 'kembali',
                            'sisa', 'tanggal_jatuh_tempo']


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ['id', 'barang', 'pembelian',
                  'diskon', 'harga_supplier', 'jumlah',
                  'subtotal', 'keterangan']
        read_only_fields = ['subtotal', 'pembelian']


class HutangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hutang
        fields = [
            'id',
            'nomor',
            'pembelian',
            'pembayaran',
            'tanggal',
            'jumlah',
            'sisa'
        ]
        read_only_fields = ['pembelian', 'pembayaran', 'sisa',]


class PembelianSerializer(serializers.ModelSerializer):
    _pembayaran_metode = serializers.SerializerMethodField("get_pembayaran_metode")
    _pembayaran_is_paid = serializers.SerializerMethodField("get_pembayaran_is_paid")

    def get_pembayaran_metode(self, value: Pembelian):
        return value.get_pembayaran_pembelian.metode

    def get_pembayaran_is_paid(self, value: Pembelian):
        return value.get_pembayaran_pembelian.is_paid

    class Meta:
        model = Pembelian
        fields = ['id',
                  'nomor',
                  'tanggal',
                  'supplier',
                  'is_published',
                  '_pembayaran_metode',
                  '_pembayaran_is_paid']
        read_only_fields = ['is_published']


