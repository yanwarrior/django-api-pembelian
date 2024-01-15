from supplier.repositories import SupplierRepository


class SupplierService:

    def __init__(self):
        self.repository = SupplierRepository()

    def get_or_create_supplier(self):
        return self.repository.get_or_create_suppier()