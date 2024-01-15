from datetime import timedelta

from django.db.models.functions import datetime
from rest_framework.exceptions import PermissionDenied

from mysite.helpers import generate_nomor
from pembelian.models import Pembayaran, Item, Pembelian, Hutang
from supplier.services import SupplierService


class PembelianRepository:

    def init_pembelian(self):
        supplier, status = SupplierService().get_or_create_supplier()
        pembelian = Pembelian.objects.create(
            nomor=generate_nomor("BLI", Pembelian.objects.all()),
            tanggal=datetime.datetime.now(),
            supplier=supplier
        )
        PembayaranRepository().create_pembayaran(pembelian)
        return pembelian

    def cegat_draft(self, pembelian):
        if not pembelian.is_published:
            raise PermissionDenied("Proses tidak diizinkan, pembelian masih dalam bentuk draft.")

    def cegat_publikasi(self, pembelian):
        if pembelian.is_published:
            raise PermissionDenied("Proses tidak diizinkan, pembelian sudah terpublikasi.")

    def validate_complete(self, pembelian: Pembelian):
        self.cegat_publikasi(pembelian)
        ItemRepository().pembelian_has_items(pembelian)
        if pembelian.get_pembayaran_pembelian.dibayar == 0:
            raise PermissionDenied("Proses tidak diziinkan, pembelian belum dibayar.")

        if pembelian.get_pembayaran_pembelian.metode == Pembayaran.KREDIT and \
                pembelian.get_pembayaran_pembelian.tempo == 0:
            raise PermissionDenied("Proses tidak diziinkan, jatuh tempo pembayaran belum diatur.")


class PembayaranRepository:

    def calculate_discount_ppn(self, diskon, ppn, total):
        if total:
            total_after_diskon = total - (total * (diskon / 100))
            return total_after_diskon + (total_after_diskon * (ppn / 100))

        return total

    def create_pembayaran(self, pembelian):
        nomor_generator = generate_nomor("PBR", Pembayaran.objects.all())
        return Pembayaran.objects.create(pembelian=pembelian, nomor=nomor_generator,
                                         diskon=0, ppn=0,
                                         total=0, is_paid=False,
                                         dibayar=0, kembali=0,
                                         sisa=0, tempo=0)

    def get_total_item(self, pembayaran):
        total = 0
        items = Item.objects.filter(pembelian=pembayaran.pembelian)

        if items:
            for item in items:
                total = total + item.subtotal

        return self.calculate_discount_ppn(pembayaran.diskon, pembayaran.ppn, total)

    def get_kembali_pembayaran(self, pembayaran, total):
        if total == 0:
            return 0

        kembali = pembayaran.dibayar - total

        if kembali < 0:
            return 0

        return kembali

    def get_sisa_pembayaran(self, pembayaran, total):
        if total == 0:
            return 0

        sisa = pembayaran.dibayar - total

        if sisa < 0:
            # Hutang berlaku jika sisa kurang dari 0 (-negatif)
            return abs(sisa)

        # Hutang tidak berlaku, dianggap lunas (Tunai)
        # jika sisa >= 0
        return 0

    def get_paid_pembayaran(self, pembayaran, total):
        if total == 0:
            return False

        if pembayaran.dibayar < total:
            return False
        return True

    def get_metode_pembayaran(self, sisa, total):
        if total == 0:
            return Pembayaran.TUNAI

        if sisa > 0:
            return Pembayaran.KREDIT
        return Pembayaran.TUNAI

    def get_jatuh_tempo(self, pembayaran, status):
        if pembayaran.tempo == 0:
            return None

        if status == Pembayaran.KREDIT:
            return pembayaran.pembelian.tanggal.date() + timedelta(days=pembayaran.tempo)
        return None

    def get_tempo(self, status, current_tempo):
        if status == Pembayaran.KREDIT:
            return current_tempo
        return 0

    def update_pembayaran(self, pembayaran):
        total = self.get_total_item(pembayaran)
        kembali = self.get_kembali_pembayaran(pembayaran, total)
        sisa = self.get_sisa_pembayaran(pembayaran, total)
        is_paid = self.get_paid_pembayaran(pembayaran, total)
        metode = self.get_metode_pembayaran(sisa, total)
        tanggal_jatuh_tempo = self.get_jatuh_tempo(pembayaran, metode)
        tempo = self.get_tempo(metode, pembayaran.tempo)

        pembayaran.total = total
        pembayaran.kembali = kembali
        pembayaran.sisa = sisa
        pembayaran.is_paid = is_paid
        pembayaran.metode = metode
        pembayaran.tanggal_jatuh_tempo = tanggal_jatuh_tempo
        pembayaran.tempo = tempo
        return pembayaran.save()



class ItemRepository:

    def get_subtotal(self, item):
        subtotal = (item['harga_supplier'] - item['diskon']) * item['jumlah']
        return subtotal if subtotal >= 0 else 0

    def pembelian_has_items(self, pembelian):
        if not Item.objects.filter(pembelian=pembelian).exists():
            raise PermissionDenied(detail='Pembelian tidak memiliki items.')


class HutangRepository:

    def create_hutang(self, pembayaran: Pembayaran):
        if pembayaran.metode == Pembayaran.KREDIT:
            return Hutang.objects.create(
                nomor=generate_nomor("HTG", Hutang.objects.all()),
                pembelian=pembayaran.pembelian,
                pembayaran=pembayaran,
                tanggal=pembayaran.pembelian.tanggal + timedelta(days=pembayaran.tempo),
                jumlah=0,
                sisa=pembayaran.sisa,
            )

    def bayar_hutang(self, hutang):
        pembayaran = hutang.pembayaran
        sisa = hutang.sisa - hutang.jumlah

        if sisa <= 0:
            pembayaran.is_paid = True
            pembayaran.save()
            hutang.sisa = 0
        else:
            hutang.sisa = sisa

        hutang.save()

