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
        fields = ['id', 'nomor', 'pembelian',
                  'pembayaran', 'tanggal', 'jumlah',
                  'sisa']
        read_only_fields = ['pembelian', 'pembayaran', 'sisa']


class PembelianSerializer(serializers.ModelSerializer):
    meta_pembayaran = serializers.SerializerMethodField('get_pembayaran')

    def get_pembayaran(self, value: Pembelian):
        pembayaran = value.get_pembayaran_pembelian
        return {'id': pembayaran.id, 'nomor': pembayaran.nomor,
                'metode': pembayaran.metode, 'diskon': pembayaran.diskon,
                'ppn': pembayaran.ppn, 'total': pembayaran.total,
                'is_paid': pembayaran.is_paid, 'dibayar': pembayaran.dibayar,
                'kembali': pembayaran.kembali, 'sisa': pembayaran.sisa,
                'tempo': pembayaran.tempo, 'tanggal_jatuh_tempo': pembayaran.tanggal_jatuh_tempo,
                'hutang': pembayaran.hutang_set.all()}

    class Meta:
        model = Pembelian
        fields = ['id', 'nomor',
                  'tanggal', 'supplier',
                  'is_published', 'meta_pembayaran']
        read_only_fields = ['is_published']


