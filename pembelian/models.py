from django.db import models

from barang.models import Barang
from supplier.models import Supplier


class Pembelian(models.Model):
    nomor = models.CharField(max_length=10, unique=True)
    tanggal = models.DateTimeField()
    supplier = models.ForeignKey(Supplier, related_name='populate_pembelian_supplier', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.nomor


class Pembayaran(models.Model):
    TUNAI = "tunai"
    KREDIT = "kredit"
    METODE_PEMBELIAN = {
        TUNAI: "Tunai",
        KREDIT: "Kredit"
    }

    nomor = models.CharField(max_length=10, unique=True)
    pembelian = models.OneToOneField(Pembelian, on_delete=models.CASCADE, related_name='get_pembayaran_pembelian')
    metode = models.CharField(max_length=100, choices=METODE_PEMBELIAN, default=TUNAI)
    diskon = models.PositiveIntegerField()
    ppn = models.PositiveIntegerField()
    total_ppn_discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=False)

    dibayar = models.PositiveIntegerField()
    kembali = models.PositiveIntegerField()

    def __str__(self):
        return self.pembelian.nomor


class Hutang(models.Model):
    nomor = models.CharField(max_length=10, unique=True)
    pembelian = models.OneToOneField(Pembelian, on_delete=models.CASCADE, related_name='get_hutang_pembelian')
    pembayaran = models.OneToOneField(Pembayaran, on_delete=models.CASCADE, related_name='get_hutang_pembayaran')
    tempo = models.PositiveIntegerField()
    sisa = models.PositiveIntegerField()

    def __str__(self):
        return self.pembelian.nomor


class Item(models.Model):
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='populate_item_barang')
    pembelian = models.ForeignKey(Pembelian, on_delete=models.CASCADE, related_name='populate_item_pembelian')
    diskon = models.PositiveIntegerField()
    harga_supplier = models.PositiveIntegerField()
    jumlah = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    keterangan = models.CharField(max_length=200)

    def __str__(self):
        return self.pembelian.nomor
