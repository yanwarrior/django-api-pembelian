from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pembelian.filters import PembelianFilter, ItemFilter, ReturPembelianFilter, ReturItemPembelianFilter
from pembelian.helpers import pembelian_init, publish_pembelian, calculate_pembayaran, calculate_item, calculate_hutang, \
    stok_masuk_records, retur_pembelian_init, publish_retur_pembelian, stok_retur_records
from pembelian.models import Pembelian, Pembayaran, Item, Hutang, ReturPembelian, ReturItemPembelian
from pembelian.serializers import PembelianSerializer, PembayaranSerializer, ItemSerializer, HutangSerializer, \
    ReturPembelianSerializer, ReturItemPembelianSerializer


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
        serializer = PembelianSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        pembelian = pembelian_init(request)
        serializer = PembelianSerializer(pembelian)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_detail(request, pk):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(pk=pk)
        except Pembelian.DoesNotExist:
            raise Http404

        serializer = PembelianSerializer(pembelian)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            pembelian = Pembelian.objects.get(pk=pk, is_draft=True)
        except Pembelian.DoesNotExist:
            raise Http404

        serializer = PembelianSerializer(pembelian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            calculate_pembayaran(pembelian.pembayaran_pembelian)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            pembelian = Pembelian.objects.get(pk=pk, is_draft=True)
        except Pembelian.DoesNotExist:
            raise Http404

        pembelian.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_choice(request, nomor):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(nomor=nomor)
        except Pembelian.DoesNotExist:
            raise Http404

        serializer = PembelianSerializer(pembelian)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembelian_publish(request, pk):
    try:
        pembelian = Pembelian.objects.get(pk=pk, is_draft=True)
    except Pembelian.DoesNotExist:
        raise Http404

    pembelian = publish_pembelian(pembelian)
    stok_masuk_records(pembelian)
    serializer = PembelianSerializer(pembelian)

    return Response(serializer.data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pembayaran_detail(request, pk):
    if request.method == 'GET':
        try:
            pembayaran = Pembayaran.objects.get(pembelian__pk=pk)
        except Pembayaran.DoesNotExist:
            raise Http404

        serializer = PembayaranSerializer(pembayaran)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            pembayaran = Pembayaran.objects.get(pembelian__pk=pk, pembelian__is_draft=True)
        except Pembayaran.DoesNotExist:
            raise Http404
        serializer = PembayaranSerializer(pembayaran, data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            calculate_pembayaran(instance)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def item_list(request, pk):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(pk=pk)
        except Pembelian.DoesNotExist:
            raise Http404

        paginator = PageNumberPagination()
        daftar_item = Item.objects.filter(pembelian=pembelian)
        filterset = ItemFilter(request.GET, queryset=daftar_item)

        if filterset.is_valid():
            daftar_item = filterset.qs

        result_page = paginator.paginate_queryset(daftar_item, request)
        serializer = ItemSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        try:
            pembelian = Pembelian.objects.get(pk=pk, is_draft=True)
        except Pembelian.DoesNotExist:
            raise Http404

        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(pembelian=pembelian)
            item = calculate_item(instance)
            calculate_pembayaran(item.pembelian.pembayaran_pembelian)
            serializer = ItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def item_detail(request, pk, item_pk):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(pk=pk)
            item = Item.objects.get(pk=item_pk, pembelian=pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except Item.DoesNotExist:
            raise Http404

        serializer = ItemSerializer(item)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            pembelian = Pembelian.objects.get(pk=pk, is_draft=True)
            item = Item.objects.get(pk=item_pk, pembelian=pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except Item.DoesNotExist:
            raise Http404

        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            item = calculate_item(instance)
            calculate_pembayaran(pembelian.pembayaran_pembelian)

            serializer = ItemSerializer(item)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            pembelian = Pembelian.objects.get(pk=pk, is_draft=True)
            item = Item.objects.get(pk=item_pk, pembelian=pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except Item.DoesNotExist:
            raise Http404

        item.delete()
        calculate_pembayaran(pembelian.pembayaran_pembelian)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def hutang_detail(request, id):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(
                is_draft=False,
                pk=id
            )
            pembayaran = Pembayaran.objects.get(
                pembelian=pembelian,
                metode=Pembayaran.PEMBAYARAN_KREDIT
            )
            print(pembayaran.pk)
            hutang = Hutang.objects.get(
                pembayaran=pembayaran,
            )
        except Pembelian.DoesNotExist:
            raise Http404
        except Pembayaran.DoesNotExist:
            raise Http404
        except Hutang.DoesNotExist:
            raise Http404

        serializer = HutangSerializer(hutang)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            pembelian = Pembelian.objects.get(
                is_draft=False,
                pk=id
            )
            pembayaran = Pembayaran.objects.get(
                pembelian=pembelian,
                metode=Pembayaran.PEMBAYARAN_KREDIT,
                lunas=False
            )
            hutang = Hutang.objects.get(pembayaran=pembayaran)
        except Pembelian.DoesNotExist:
            raise Http404
        except Pembayaran.DoesNotExist:
            raise Http404
        except Hutang.DoesNotExist:
            raise Http404

        serializer = HutangSerializer(hutang, data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            hutang = calculate_hutang(instance)
            serializer = HutangSerializer(hutang)
            return Response(serializer.data)


@api_view(['GET', 'POST',])
@permission_classes([IsAuthenticated])
@transaction.atomic
def retur_list(request, id):
    try:
        pembelian = Pembelian.objects.get(is_draft=False, pk=id)
    except Pembelian.DoesNotExist:
        raise Http404

    if request.method == 'GET':

        paginator = PageNumberPagination()
        daftar_retur_pembelian = ReturPembelian.objects.filter(pembelian=pembelian)
        filterset = ReturPembelianFilter(request.GET, queryset=daftar_retur_pembelian)

        if filterset.is_valid():
            daftar_retur_pembelian = filterset.qs

        result_page = paginator.paginate_queryset(daftar_retur_pembelian, request)
        serializer = ReturPembelianSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':

        retur_pembelian = retur_pembelian_init(pembelian, request)
        serializer = ReturPembelianSerializer(retur_pembelian)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def retur_detail(request, id, retur_id):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(is_draft=False, pk=id)
            retur_pembelian = ReturPembelian.objects.get(pk=retur_id, pembelian=pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except ReturPembelian.DoesNotExist:
            raise Http404

        serializer = ReturPembelianSerializer(retur_pembelian)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            pembelian = Pembelian.objects.get(is_draft=False, pk=id)
            retur_pembelian = ReturPembelian.objects.get(pk=retur_id, is_draft=True, pembelian=pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except ReturPembelian.DoesNotExist:
            raise Http404

        serializer = ReturPembelianSerializer(retur_pembelian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            pembelian = Pembelian.objects.get(is_draft=False, pk=id)
            retur_pembelian = ReturPembelian.objects.get(pk=retur_id, is_draft=True, pembelian=pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except ReturPembelian.DoesNotExist:
            raise Http404

        retur_pembelian.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def retur_published(request, id, retur_id):
    try:
        pembelian = Pembelian.objects.get(is_draft=False, pk=id)
        retur_pembelian = ReturPembelian.objects.get(pk=retur_id, is_draft=True, pembelian=pembelian)
    except Pembelian.DoesNotExist:
        raise Http404
    except ReturPembelian.DoesNotExist:
        raise Http404

    retur_pembelian = publish_retur_pembelian(retur_pembelian)
    stok_retur_records(retur_pembelian)
    serializer = ReturPembelianSerializer(retur_pembelian)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def retur_item_list(request, id, retur_id):
    try:
        pembelian = Pembelian.objects.get(is_draft=False, pk=id)
        retur_pembelian = ReturPembelian.objects.get(pk=retur_id, pembelian=pembelian)
    except Pembelian.DoesNotExist:
        raise Http404
    except ReturPembelian.DoesNotExist:
        raise Http404

    paginator = PageNumberPagination()
    daftar_item_retur_pembelian = ReturItemPembelian.objects.filter(retur_pembelian=retur_pembelian)
    filterset = ReturItemPembelianFilter(request.GET, queryset=daftar_item_retur_pembelian)

    if filterset.is_valid():
        daftar_item_retur_pembelian = filterset.qs

    result_page = paginator.paginate_queryset(daftar_item_retur_pembelian, request)
    serializer = ReturItemPembelianSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def retur_item_detail(request, id, retur_id, item_id):
    if request.method == 'GET':
        try:
            pembelian = Pembelian.objects.get(is_draft=False, pk=id)
            retur_pembelian = ReturPembelian.objects.get(pk=retur_id, pembelian=pembelian)
            retur_item_pembelian = ReturItemPembelian.objects.get(pk=item_id, retur_pembelian=retur_pembelian)
        except Pembelian.DoesNotExist:
            raise Http404
        except ReturPembelian.DoesNotExist:
            raise Http404
        except ReturItemPembelian.DoesNotExist:
            raise Http404

        serializer = ReturItemPembelianSerializer(retur_item_pembelian)
        return Response(serializer.data)

    try:
        pembelian = Pembelian.objects.get(is_draft=False, pk=id)
        retur_pembelian = ReturPembelian.objects.get(pk=retur_id, pembelian=pembelian, is_draft=True)
        retur_item_pembelian = ReturItemPembelian.objects.get(pk=item_id, retur_pembelian=retur_pembelian)
    except Pembelian.DoesNotExist:
        raise Http404
    except ReturPembelian.DoesNotExist:
        raise Http404
    except ReturItemPembelian.DoesNotExist:
        raise Http404

    if request.method == 'PUT':
        serializer = ReturItemPembelianSerializer(retur_item_pembelian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        retur_item_pembelian.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
