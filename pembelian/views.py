from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pembelian.filters import PembelianFilter, ItemFilter, HutangFilter
from pembelian.models import Pembelian, Pembayaran, Item, Hutang
from pembelian.permissions import PreventPublishedPermission, OnlyKreditPermission, \
    OnlyPublishedPermission
from pembelian.serializers import PembelianSerializer, PembayaranSerializer, ItemSerializer, HutangSerializer
from pembelian.services import PembayaranService, ItemService, HutangService, PembelianService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_init(request):
    pembelian = PembelianService.factory().init_pembelian()
    serializer = PembelianSerializer(pembelian)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
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
        serializer = PembelianSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


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
        # Pembelian yang statusnya sudah dipublikasikan tidak diizinkan/harus dicegah
        PembelianService.factory().cegat_publikasi(pembelian)

        serializer = PembelianSerializer(pembelian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_complete(request, pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk)
    except Pembelian.DoesNotExist:
        raise Http404

    # Validate pembelian apakah sudah memenuhi syarat atau belum
    PembelianService.factory().validate_complete(pembelian)

    pembelian.is_published = True
    pembelian.save()
    serializer = PembelianSerializer(pembelian)
    # Kalkulasi pembayaran
    PembayaranService().update_pembayaran(pembelian.get_pembayaran_pembelian)
    # Create hutang
    HutangService.factory().create_hutang(pembayaran=pembelian.get_pembayaran_pembelian)

    return Response(serializer.data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembayaran_detail(request, pk):
    try:
        pembayaran = Pembayaran.objects.get(pembelian__pk=pk)
    except Pembayaran.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = PembayaranSerializer(pembayaran)
        return Response(serializer.data)

    if request.method == 'PUT':
        # Cegat pembelian yang sudah terpublikasi
        PembelianService().cegat_publikasi(pembayaran.pembelian)
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
        # Cegat pembelian yang sudah terpublikasi
        PembelianService().cegat_publikasi(pembelian)

        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            # Setelah item dari client valid, kalkukasi subtotalnya
            subtotal = ItemService().get_subtotal(serializer.validated_data)
            instance = serializer.save(subtotal=subtotal, pembelian=pembelian)
            # Selanjutnya, update pembayaran
            PembayaranService().update_pembayaran(instance.pembelian.get_pembayaran_pembelian)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, PreventPublishedPermission])
@transaction.atomic
def item_detail(request, pk, item_pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk)
        item = Item.objects.get(pk=item_pk, pembelian=pembelian)
    except Pembelian.DoesNotExist:
        raise Http404
    except Item.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            # Setelah item dari client valid, kalkukasi subtotalnya
            subtotal = ItemService().get_subtotal(serializer.validated_data)
            instance = serializer.save(subtotal=subtotal, pembelian=pembelian)
            # Selanjutnya, update pembayaran
            PembayaranService().update_pembayaran(pembelian.get_pembayaran_pembelian)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        item.delete()
        # Selanjutnya, update pembayaran
        PembayaranService().update_pembayaran(pembelian.get_pembayaran_pembelian)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, OnlyPublishedPermission, OnlyKreditPermission])
@transaction.atomic
def hutang_list(request, pk, pembayaran_pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk)
        pembayaran = Pembayaran.objects.get(pk=pembayaran_pk, pembelian=pembelian)
    except Pembelian.DoesNotExist:
        raise Http404
    except Pembayaran.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        paginator = PageNumberPagination()
        daftar_hutang = Hutang.objects.filter(pembelian=pembelian, pembayaran=pembayaran)
        filterset = HutangFilter(request.GET, queryset=daftar_hutang)

        if filterset.is_valid():
            daftar_hutang = filterset.qs

        result_page = paginator.paginate_queryset(daftar_hutang, request)
        serializer = HutangSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        serializer = HutangSerializer(data=request.data)

        if serializer.is_valid():
            hutang = serializer.save(
                pembayaran=pembayaran,
                pembelian=pembelian,
                sisa=0
            )
            # HutangService().bayar_hutang(pembayaran, hutang)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def hutang_detail(request, pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk)
        hutang = Hutang.objects.get(pembelian=pembelian)
    except Pembelian.DoesNotExist:
        raise Http404
    except Hutang.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = HutangSerializer(hutang)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = HutangSerializer(hutang, data=request.data)
        if serializer.is_valid():
            serializer.save()
            HutangService().factory().bayar_hutang(hutang)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)