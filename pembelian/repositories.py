from mysite.helpers import generate_nomor
from pembelian.models import Pembayaran, Item


class PembayaranRepository:
    def create_pembayaran_after_make_pembelian(self, pembelian):
        nomor_generator = generate_nomor("PBR", Pembayaran.objects.all())
        return Pembayaran.objects.create(pembelian=pembelian, nomor=nomor_generator,
                                         diskon=0, ppn=0,
                                         total_ppn_discount=0, total=0,
                                         is_paid=False, dibayar=0,
                                         kembali=0, sisa=0,
                                         tempo=0)

    def get_total_item(self, pembayaran):
        total = 0
        items = Item.objects.filter(pembelian=pembayaran.pembelian)

        if items:
            for item in items:
                total = total + item.subtotal

        if total:
            total_diskon = total - pembayaran.diskon
            total_ppn = total_diskon * (pembayaran.ppn / 100)
            total = total_ppn + total_diskon

        return total

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

    def update_pembayaran(self, pembayaran):
        total = self.get_total_item(pembayaran)
        kembali = self.get_kembali_pembayaran(pembayaran, total)
        sisa = self.get_sisa_pembayaran(pembayaran, total)
        is_paid = self.get_paid_pembayaran(pembayaran, total)
        metode = self.get_metode_pembayaran(sisa, total)

        pembayaran.total = total
        pembayaran.kembali = kembali
        pembayaran.sisa = sisa
        pembayaran.is_paid = is_paid
        pembayaran.metode = metode
        return pembayaran.save()

class ItemRepository:
    def get_subtotal(self, item):
        subtotal = (item['harga_supplier'] - item['diskon']) * item['jumlah']
        return subtotal if subtotal >= 0 else 0


