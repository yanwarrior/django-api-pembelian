from django.contrib.auth.models import User
from django.db import models

from barang.models import Barang
from supplier.models import Supplier


class Pembelian(models.Model):
    nomor = models.CharField(max_length=7, unique=True)
    tanggal = models.DateField(auto_created=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='daftar_pembelian_supplier')
    is_draft = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daftar_pembelian_user')

    def __str__(self):
        return self.nomor


class Pembayaran(models.Model):
    PEMBAYARAN_TUNAI = 'tunai'
    PEMBAYARAN_KREDIT = 'kredit'
    METODE_CHOICE = {
        PEMBAYARAN_TUNAI: 'Tunai',
        PEMBAYARAN_KREDIT: 'Kredit'
    }
    nomor = models.CharField(max_length=7, unique=True)
    tanggal = models.DateField(auto_now_add=True)
    pembelian = models.OneToOneField(Pembelian, on_delete=models.CASCADE, related_name='pembayaran_pembelian')
    total = models.PositiveIntegerField(default=0)
    ppn = models.PositiveIntegerField(default=0)
    diskon = models.PositiveIntegerField(default=0)
    dibayar = models.PositiveIntegerField(default=0)
    sisa = models.PositiveIntegerField(default=0)
    kembali = models.PositiveIntegerField(default=0)
    metode = models.CharField(max_length=8, choices=METODE_CHOICE, default=PEMBAYARAN_TUNAI)
    lunas = models.BooleanField(default=False)
    tempo = models.PositiveSmallIntegerField(default=3)
    jatuh_tempo = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nomor


class Hutang(models.Model):
    nomor = models.CharField(max_length=7, unique=True)
    pembayaran = models.OneToOneField(Pembayaran, on_delete=models.CASCADE, related_name='hutang_pembayaran')
    tanggal = models.DateField(auto_now_add=True)
    dibayar = models.PositiveIntegerField(default=0)
    sisa = models.PositiveIntegerField(default=0)
    keterangan = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nomor


class Item(models.Model):
    pembelian = models.ForeignKey(Pembelian, on_delete=models.CASCADE, related_name='daftar_item_pembelian')
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='daftar_item_barang')
    harga = models.PositiveIntegerField(default=0)
    diskon = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.barang.nomor


class ReturPembelian(models.Model):
    nomor = models.CharField(max_length=7, unique=True)
    pembelian = models.ForeignKey(Pembelian, related_name='retur_pembelian_pembelian', on_delete=models.PROTECT)
    tanggal = models.DateField(auto_created=True)
    is_draft = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='daftar_return_pembelian_user', on_delete=models.PROTECT)

    def __str__(self):
        return self.nomor


class ReturItemPembelian(models.Model):
    retur_pembelian = models.ForeignKey(
        ReturPembelian,
        on_delete=models.CASCADE,
        related_name='daftar_retur_item_pembelian_retur_pembelian'
    )
    barang = models.ForeignKey(
        Barang,
        on_delete=models.PROTECT,
        related_name='daftar_retur_item_pembelian_barang'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='daftar_retur_item_pembelian_item'
    )
    quantity = models.PositiveIntegerField(default=0)
    alasan = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.retur_pembelian.nomor
