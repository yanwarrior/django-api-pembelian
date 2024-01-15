from rest_framework import permissions

from pembelian.models import Item, Pembelian, Pembayaran


class OnlyPublishedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        try:
            pk = view.kwargs.get('pk', None)
            pembelian = Pembelian.objects.get(pk=pk)
            if pembelian.is_published:
                return True

            return False
        except Pembelian.DoesNotExist:
            return False


class OnlyDraftPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        pk = view.kwargs.get('pk', None)
        pembelian = Pembelian.objects.get(pk=pk)
        if pembelian.is_published:
            return False

        return True
        # try:
        # except Pembelian.DoesNotExist:
        #     return False

class PreventPublishedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        try:
            pk = view.kwargs.get('pk', None)
            pembelian = Pembelian.objects.get(pk=pk)
            if not pembelian.is_published:
                return True

            return False
        except Pembelian.DoesNotExist:
            return False


class AllowUnpublishedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs.get('pk', None)
            pembelian = Pembelian.objects.get(pk=pk)

            if pembelian.is_published:
                return False

            # Periksa item tersedia?
            if not Item.objects.filter(pembelian=pembelian).exists():
                return False

            # Periksa apakah pembayaran masih kosong (dibayar)
            if pembelian.get_pembayaran_pembelian.dibayar == 0:
                return False

            return True
        except Exception as e:
            return False


class OnlyKreditPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        try:
            pk = view.kwargs.get('pk', None)
            pembayaran_pk = view.kwargs.get('pembayaran_pk', None)
            pembayaran = Pembayaran.objects.get(pembelian__pk=pk, pk=pembayaran_pk)

            if pembayaran.metode == Pembayaran.KREDIT:
                return True

            return False

        except Pembayaran.DoesNotExist:
            return False