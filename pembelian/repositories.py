from datetime import timedelta

from mysite.helpers import generate_nomor
from pembelian.models import Pembayaran, Item


class PembayaranRepository:

    def calculate_discount_ppn(self, diskon, ppn, total):
        if total:
            total_after_diskon = total - (total * (diskon / 100))
            return total_after_diskon + (total_after_diskon * (ppn / 100))

        return total

    def create_pembayaran_after_make_pembelian(self, pembelian):
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


