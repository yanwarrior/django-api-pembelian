from pembelian.repositories import PembayaranRepository


class PembayaranService:

    def __init__(self):
        self.repository = PembayaranRepository()

    def create_pembayaran_after_make_pembelian(self, pembelian):
        return self.repository.create_pembayaran_after_make_pembelian(pembelian)
