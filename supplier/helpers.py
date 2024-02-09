# from supplier.models import Supplier
from mysite.helpers import generate_nomor
from supplier.models import Supplier


def get_or_create_supplier():
    supplier = Supplier.objects.filter(nama='No Supplier').first()

    if not supplier:
        supplier, status = Supplier.objects.get_or_create(
            nomor=generate_nomor("SPL", Supplier.objects.all()),
            nama="No Supplier",
        )
        return supplier

    return supplier