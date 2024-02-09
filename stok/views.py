from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from stok.filters import StokFilter
from stok.models import Stok
from stok.serializers import StokSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def stok_list(request):
    paginator = PageNumberPagination()
    daftar_stok = Stok.objects.all()
    filterset = StokFilter(request.GET, queryset=daftar_stok)

    if filterset.is_valid():
        daftar_stok = filterset.qs

    result_page = paginator.paginate_queryset(daftar_stok, request)
    serializer = StokSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

