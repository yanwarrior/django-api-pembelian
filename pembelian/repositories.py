from mysite.helpers import generate_nomor
from pembelian.models import Pembayaran


class PembayaranRepository:

    def create_pembayaran_after_make_pembelian(self, pembelian):
        return Pembayaran.objects.create(
            pembelian=pembelian,
            nomor=generate_nomor("PBR", Pembayaran.objects.all()),
            diskon=0,
            ppn=0,
            total_ppn_discount=0,
            total=0,
            is_paid=False,
            dibayar=0,
            kembali=0
        )