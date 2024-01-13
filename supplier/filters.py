import django_filters

from supplier.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            'nama': ['contains'],
            "telepon": ['exact'],
            "bank": ['exact'],
            "pic": ['contains']
        }