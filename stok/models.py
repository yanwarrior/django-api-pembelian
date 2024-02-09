from django.db import models

from barang.models import Barang


class Stok(models.Model):
    nomor = models.CharField(max_length=7, unique=True)
    nomor_transaksi = models.CharField(max_length=7)
    tanggal = models.DateTimeField(auto_now_add=True)
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='daftar_stok_barang')
    stok_awal = models.PositiveIntegerField(default=0)
    masuk = models.PositiveIntegerField(default=0)
    keluar = models.PositiveIntegerField(default=0)
    stok_akhir = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nomor
