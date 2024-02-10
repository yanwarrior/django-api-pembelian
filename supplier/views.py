from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from supplier.filters import SupplierFilter, SupplierSearch
from supplier.models import Supplier
from supplier.serializers import SupplierSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def supplier_list(request):
    if request.method == 'GET':
        paginator = PageNumberPagination()
        daftar_supplier = Supplier.objects.exclude(nama='No Supplier').filter(SupplierSearch.query(request))
        filterset = SupplierFilter(request.GET, queryset=daftar_supplier)

        if filterset.is_valid():
            daftar_supplier = filterset.qs

        result_page = paginator.paginate_queryset(daftar_supplier, request)
        serializer = SupplierSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def supplier_detail(request, id):
    try:
        supplier = Supplier.objects.get(pk=id)
    except Supplier.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        supplier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_choice(request, nomor):
    try:
        supplier = Supplier.objects.get(nomor=nomor)
    except Supplier.DoesNotExist:
        raise Http404

    serializer = SupplierSerializer(supplier)
    return Response(serializer.data)