from django.db import models


class Supplier(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    telepon = models.CharField(max_length=16)
    bank = models.CharField(max_length=5)
    rekening = models.CharField(max_length=15)
    pic = models.CharField(max_length=100)

    def __str__(self):
        return self.nama