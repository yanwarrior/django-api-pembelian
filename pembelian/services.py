from pembelian.repositories import PembayaranRepository, ItemRepository


class PembayaranService:

    def __init__(self):
        self.repository = PembayaranRepository()

    def create_pembayaran_after_make_pembelian(self, pembelian):
        return self.repository.create_pembayaran_after_make_pembelian(pembelian)

    def update_pembayaran(self, pembayaran):
        return self.repository.update_pembayaran(pembayaran)


class ItemService:
    def __init__(self):
        self.repository = ItemRepository()

    def get_subtotal(self, item):
        return self.repository.get_subtotal(item)
