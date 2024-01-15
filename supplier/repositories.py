from supplier.models import Supplier


class SupplierRepository:

    def get_or_create_suppier(self):
        supplier = Supplier.objects.get_or_create(
            nama='No Supplier',
            alamat='-',
            telepon='-',
            bank='-',
            rekening='-',
            pic='-'
        )

        return supplier