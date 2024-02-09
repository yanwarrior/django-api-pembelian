# import datetime
#
# from rest_framework.exceptions import PermissionDenied
#
# from mysite.helpers import generate_nomor
# from pembelian.models import Pembelian, Pembayaran, Item, Hutang
# from supplier.helpers import get_or_create_supplier
#
import datetime

from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from mysite.helpers import generate_nomor
from pembelian.models import Pembelian, Pembayaran, Hutang, Item, ReturPembelian, ReturItemPembelian
from stok.models import Stok
from supplier.helpers import get_or_create_supplier


def pembelian_init(request):
    supplier = get_or_create_supplier()
    user = request.user
    pembelian = Pembelian.objects.create(
        nomor=generate_nomor("BLI", Pembelian.objects.all()),
        tanggal=datetime.date.today(),
        is_draft=True,
        supplier=supplier,
        user=user
    )

    Pembayaran.objects.create(
        nomor=generate_nomor('BYR', Pembayaran.objects.all()),
        tanggal=datetime.date.today(),
        pembelian=pembelian,
    )

    return pembelian


def calculate_pembayaran(pembayaran: Pembayaran):
    pembelian = pembayaran.pembelian
    daftar_item = pembelian.daftar_item_pembelian.all()

    if not daftar_item.exists():
        raise PermissionDenied(detail='Transaksi minimal membutuhkan 1 item di dalamnya')

    total_sementara = pembelian.daftar_item_pembelian.all().aggregate(Sum('total'))
    total_sementara = total_sementara.get('total__sum', 0) if total_sementara.get('total__sum') else 0
    harga_diskon = total_sementara - (total_sementara * (pembayaran.diskon / 100))
    harga_ppn = harga_diskon + (harga_diskon * (pembayaran.ppn / 100))
    pembayaran.total = harga_ppn
    pembayaran.save()

    if pembayaran.total > pembayaran.dibayar:
        pembayaran.sisa = pembayaran.total - pembayaran.dibayar
        pembayaran.kembali = 0
        pembayaran.metode = Pembayaran.PEMBAYARAN_KREDIT
        pembayaran.tempo = pembayaran.tempo if pembayaran.tempo > 0 else 3
        pembayaran.jatuh_tempo = pembelian.tanggal + datetime.timedelta(days=pembayaran.tempo)
        pembayaran.save()
    else:
        pembayaran.kembali = pembayaran.dibayar - pembayaran.total
        pembayaran.sisa = 0
        pembayaran.metode = Pembayaran.PEMBAYARAN_TUNAI
        pembayaran.tempo = 0
        pembayaran.jatuh_tempo = None
        pembayaran.save()

    return pembayaran


def calculate_hutang(hutang: Hutang):
    pembayaran = hutang.pembayaran
    sisa_hutang = pembayaran.sisa - hutang.dibayar

    if sisa_hutang <= 0:
        pembayaran.lunas = True
        pembayaran.sisa = 0
        pembayaran.save()

    if sisa_hutang > 0:
        pembayaran.lunas = False
        pembayaran.sisa = abs(sisa_hutang)
        pembayaran.save()
        hutang.dibayar = 0
        hutang.sisa = sisa_hutang
        hutang.save()

    return hutang


def publish_pembelian(pembelian: Pembelian):
    daftar_items = pembelian.daftar_item_pembelian.all()

    if not daftar_items.exists():
        raise PermissionDenied(detail='Item pembelian masih kosong')

    if not pembelian.pembayaran_pembelian:
        raise PermissionDenied(detail='Pembayaran masih kosong')

    if pembelian.pembayaran_pembelian.total == 0:
        raise PermissionDenied(detail='Total pembayaran masih 0')

    pembayaran = calculate_pembayaran(pembelian.pembayaran_pembelian)

    if pembayaran.metode == Pembayaran.PEMBAYARAN_KREDIT:
        pembayaran.lunas = False
        pembayaran.save()
        create_hutang(pembayaran)

    if pembayaran.metode == Pembayaran.PEMBAYARAN_TUNAI:
        pembayaran.lunas = True
        pembayaran.save()

    pembelian.is_draft = False
    pembelian.save()

    return pembelian


def calculate_item(item: Item):
    jumlah_item = Item.objects.filter(barang=item.barang, pembelian=item.pembelian).count()
    if jumlah_item > 1:
        raise PermissionDenied(detail='Item duplikasi')

    harga_diskon = item.harga - (item.harga * (item.diskon / 100))
    item.total = harga_diskon * item.quantity
    item.save()

    return item


def create_hutang(pembayaran: Pembayaran):
    hutang = Hutang.objects.create(
        nomor=generate_nomor('HTG', Hutang.objects.all()),
        pembayaran=pembayaran,
    )
    return hutang


def stok_masuk_records(pembelian: Pembelian):
    """
    Dijakankan pada saat pembelian di publikasi
    untuk menaikkan stok barang
    """
    daftar_items = pembelian.daftar_item_pembelian.all()
    bulk_data_stok = []
    counter = 1

    for item in daftar_items:
        stok_akhir = item.barang.stok + item.quantity
        stok_awal = item.barang.stok

        bulk_data_stok.append(
            Stok(
                nomor=generate_nomor('STK', Stok.objects.all(), counter),
                nomor_transaksi=pembelian.nomor,
                tanggal=datetime.datetime.now(), # TODO: timezone area for date and time
                barang=item.barang,
                stok_awal=stok_awal,
                masuk=item.quantity,
                stok_akhir=stok_akhir
            )
        )
        item.barang.stok = stok_akhir
        item.barang.save()
        counter = counter + 1

    stok = Stok.objects.bulk_create(bulk_data_stok)

    return stok


def retur_pembelian_init(pembelian: Pembelian, request):
    """
    Dijalankan pada saat membuat retur dengan post
    dan berlaku jika masih draft dan pembelian sudah terpublikasi
    """
    daftar_item = pembelian.daftar_item_pembelian.all()
    retur_pembelian = ReturPembelian.objects.create(
        nomor=generate_nomor('RTB', ReturPembelian.objects.all()),
        pembelian=pembelian,
        tanggal=timezone.now().date(),
        user=request.user
    )

    bulk_data_retur_item = []

    for item in daftar_item:
        bulk_data_retur_item.append(
            ReturItemPembelian(
                retur_pembelian=retur_pembelian,
                barang=item.barang,
                item=item,
                quantity=0
            )
        )

    ReturItemPembelian.objects.bulk_create(bulk_data_retur_item)

    return retur_pembelian


def publish_retur_pembelian(retur_pembelian: ReturPembelian):
    """
    Dijalankan pada saat retur dipublikasi
    dan berlaku jika retur masih draft dan pembelian sudah terpublikasi.
    """

    daftar_retur_item_pembelian = retur_pembelian.daftar_retur_item_pembelian_retur_pembelian.filter(quantity__gte=1)

    if not daftar_retur_item_pembelian.exists():
        raise PermissionDenied(detail='Belum ada quantity retur yang diisi')

    for retur_item_pembelian in daftar_retur_item_pembelian:
        if retur_item_pembelian.quantity > retur_item_pembelian.item.quantity:
            raise PermissionDenied(detail='Ada beberapa quantity retur yang melebihi batas quantity item')

    daftar_retur_item_pembelian = retur_pembelian.daftar_retur_item_pembelian_retur_pembelian.filter(quantity__lte=0)

    daftar_retur_item_pembelian.delete()

    retur_pembelian.is_draft = False
    retur_pembelian.save()

    return retur_pembelian


def stok_retur_records(retur_pembelian: ReturPembelian):
    """
    Dijalankan pada saat retur di publikasi setelah menjalankan publish_retur_pembelian
    untuk mengurangi stok barang
    """

    daftar_retur_item_pembelian = retur_pembelian.daftar_retur_item_pembelian_retur_pembelian.all()
    bulk_data_stok = []
    counter = 1
    for retur_item_pembelian in daftar_retur_item_pembelian:
        stok_akhir = retur_item_pembelian.barang.stok - retur_item_pembelian.quantity
        stok_awal = retur_item_pembelian.barang.stok
        bulk_data_stok.append(
            Stok(
                nomor=generate_nomor('STK', Stok.objects.all(), counter),
                nomor_transaksi=retur_pembelian.nomor,
                tanggal=retur_pembelian.tanggal,
                barang=retur_item_pembelian.barang,
                stok_awal=stok_awal,
                keluar=retur_item_pembelian.quantity,
                stok_akhir=stok_akhir
            )
        )

        retur_item_pembelian.barang.stok = stok_akhir
        retur_item_pembelian.barang.save()
        counter += 1

    Stok.objects.bulk_create(bulk_data_stok)

