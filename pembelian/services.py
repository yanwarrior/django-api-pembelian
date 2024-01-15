from pembelian.models import Pembelian
from pembelian.repositories import PembayaranRepository, ItemRepository, HutangRepository, PembelianRepository


class PembelianService:
    def __init__(self):
        self.repository = PembelianRepository()

    def init_pembelian(self):
        return self.repository.init_pembelian()

    def cegat_draft(self, pembelian):
        self.repository.cegat_draft(pembelian)

    def cegat_publikasi(self, pembelian):
        self.repository.cegat_publikasi(pembelian)

    def validate_complete(self, pembelian: Pembelian):
        self.repository.validate_complete(pembelian)

    @staticmethod
    def factory():
        return PembelianService()


class PembayaranService:

    def __init__(self):
        self.repository = PembayaranRepository()

    def create_pembayaran(self, pembelian):
        return self.repository.create_pembayaran(pembelian)

    def update_pembayaran(self, pembayaran):
        return self.repository.update_pembayaran(pembayaran)


class ItemService:
    def __init__(self):
        self.repository = ItemRepository()

    def get_subtotal(self, item):
        return self.repository.get_subtotal(item)


class HutangService:
    def __init__(self):
        self.repository = HutangRepository()

    def create_hutang(self, pembayaran):
        self.repository.create_hutang(pembayaran)

    def bayar_hutang(self, hutang):
        self.repository.bayar_hutang(hutang)

    @staticmethod
    def factory():
        return HutangService()
