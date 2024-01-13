from django.db import transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pembelian.filters import PembelianFilter
from pembelian.models import Pembelian
from pembelian.serializers import PembelianSerializer
from pembelian.services import PembayaranService


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_list(request):
    if request.method == 'GET':
        paginator = PageNumberPagination()
        daftar_pembelian = Pembelian.objects.all()
        filterset = PembelianFilter(request.GET, queryset=daftar_pembelian)

        if filterset.is_valid():
            daftar_pembelian = filterset.qs

        result_page = paginator.paginate_queryset(daftar_pembelian, request)
        serializer = PembelianSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        serializer = PembelianSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            # Setelah pembelian berhasil, buat objek pembayaran
            PembayaranService().create_pembayaran_after_make_pembelian(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


