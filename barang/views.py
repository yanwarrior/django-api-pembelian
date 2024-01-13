from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from barang.filters import BarangFilter
from barang.helpers import generate_nomor
from barang.models import Barang
from barang.serializers import BarangSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def barang_list(request):
    if request.method == 'GET':
        paginator = PageNumberPagination()
        daftar_barang = Barang.objects.all()
        filterset = BarangFilter(request.GET, queryset=daftar_barang)
        if filterset.is_valid():
            daftar_barang = filterset.qs
        result_page = paginator.paginate_queryset(daftar_barang, request)
        serializer = BarangSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        serializer = BarangSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def barang_detail(request, id):
    try:
        barang = Barang.objects.get(id=id)
    except Barang.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = BarangSerializer(barang)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = BarangSerializer(barang, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        barang.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def barang_number(request):
    return Response({"detail": generate_nomor("BRG", Barang.objects.all())})