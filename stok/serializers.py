from rest_framework import serializers

from stok.models import Stok


class StokSerializer(serializers.ModelSerializer):
    jam_masuk = serializers.SerializerMethodField('get_jam_masuk')
    jam_keluar = serializers.SerializerMethodField('get_jam_keluar')
    nomor_barang = serializers.SerializerMethodField('get_nomor_barang')
    nama_barang = serializers.SerializerMethodField('get_nama_barang')
    stok_real = serializers.SerializerMethodField('get_stok_real')

    def get_jam_masuk(self, value: Stok):
        if value.masuk:
            return value.tanggal.strftime("%H:%M:%S")
        return None

    def get_jam_keluar(self, value: Stok):
        if value.keluar:
            return value.tanggal.strftime("%H:%M:%S")
        return None

    def get_nomor_barang(self, value: Stok):
        return value.barang.nomor

    def get_nama_barang(self, value: Stok):
        return value.barang.nama

    def get_stok_real(self, value: Stok):
        return value.barang.stok

    class Meta:
        model = Stok
        fields = [
            'id',
            'nomor',
            'nomor_transaksi',
            'tanggal',
            'barang',
            'stok_awal',
            'masuk',
            'keluar',
            'stok_akhir',
            'jam_masuk',
            'jam_keluar',
            'nomor_barang',
            'nama_barang',
            'stok_real'
        ]