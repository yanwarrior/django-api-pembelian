from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pembelian.filters import PembelianFilter, ItemFilter
from pembelian.models import Pembelian, Pembayaran, Item
from pembelian.serializers import PembelianSerializer, PembayaranSerializer, ItemSerializer
from pembelian.services import PembayaranService, ItemService


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


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_detail(request, pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk)
    except Pembelian.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = PembelianSerializer(pembelian)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = PembelianSerializer(pembelian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembayaran_detail(request, pk):
    try:
        pembayaran = Pembayaran.objects.get(pembelian__pk=pk)
    except Pembelian.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = PembayaranSerializer(pembayaran)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = PembayaranSerializer(pembayaran, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            # Setelah pembayaran disimpan, update juga bagian
            # seperti metode, total, is_paid, dll...
            PembayaranService().update_pembayaran(instance)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def item_list(request, pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk)
    except Pembelian.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        paginator = PageNumberPagination()
        daftar_item = Item.objects.filter(pembelian=pembelian)
        filterset = ItemFilter(request.GET, queryset=daftar_item)

        if filterset.is_valid():
            daftar_item = filterset.qs

        result_page = paginator.paginate_queryset(daftar_item, request)
        serializer = ItemSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            # Setelah item dari client valid, kalkukasi subtotalnya
            subtotal = ItemService().get_subtotal(serializer.validated_data)
            instance = serializer.save(subtotal=subtotal)
            # Selanjutnya, update pembayaran
            PembayaranService().update_pembayaran(instance.pembelian.get_pembayaran_pembelian)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


