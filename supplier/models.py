from django.db import models


class Supplier(models.Model):
    nomor = models.CharField(max_length=7, unique=True)
    nama = models.CharField(max_length=100)
    alamat = models.CharField(max_length=225)
    telepon = models.CharField(max_length=13)
    contact_person = models.CharField(max_length=30)
    bank = models.CharField(max_length=5)
    rekening = models.CharField(max_length=16)

    def __str__(self):
        return self.nomor