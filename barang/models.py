from django.db import models


class Barang(models.Model):
    nomor = models.CharField(max_length=100, unique=True)
    nama = models.CharField(max_length=100)
    satuan = models.CharField(max_length=50)
    jenis = models.CharField(max_length=50)
    harga_beli = models.PositiveIntegerField()
    harga_jual = models.PositiveIntegerField()
    stok = models.PositiveIntegerField()

    def __str__(self):
        return self.nomor

