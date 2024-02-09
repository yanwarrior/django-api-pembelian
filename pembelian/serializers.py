from rest_framework import serializers

from pembelian.models import Pembelian, Pembayaran, Item, Hutang, ReturPembelian, ReturItemPembelian


class PembelianSerializer(serializers.ModelSerializer):
    nama_supplier = serializers.SerializerMethodField('get_nama_supplier')
    nomor_supplier = serializers.SerializerMethodField('get_nomor_supplier')
    pembayaran_lunas = serializers.SerializerMethodField('get_pembayaran_lunas')
    jumlah_barang = serializers.SerializerMethodField('get_jumlah_barang')
    metode_pembayaran = serializers.SerializerMethodField('get_metode_pembayaran')

    def get_nama_supplier(self, value: Pembelian):
        return value.supplier.nama

    def get_nomor_supplier(self, value: Pembelian):
        return value.supplier.nomor

    def get_pembayaran_lunas(self, value: Pembelian):
        return value.pembayaran_pembelian.lunas

    def get_jumlah_barang(self, value: Pembelian):
        return value.daftar_item_pembelian.all().count()

    def get_metode_pembayaran(self, value: Pembelian):
        return value.pembayaran_pembelian.metode

    class Meta:
        model = Pembelian
        fields = [
            'id',
            'nomor',
            'tanggal',
            'supplier',
            'user',
            'is_draft',
            'nama_supplier',
            'nomor_supplier',
            'pembayaran_lunas',
            'jumlah_barang',
            'metode_pembayaran',
        ]

        read_only_fields = [
            'nomor',
            'user',
            'is_draft',
            'nama_supplier',
            'nomor_supplier',
            'pembayaran_lunas',
            'jumlah_barang',
            'metode_pembayaran',
        ]


class ItemSerializer(serializers.ModelSerializer):
    nomor_barang = serializers.SerializerMethodField('get_nomor_barang')
    nama_barang = serializers.SerializerMethodField('get_nama_barang')
    jenis = serializers.SerializerMethodField('get_jenis')
    satuan = serializers.SerializerMethodField('get_satuan')
    harga_diskon = serializers.SerializerMethodField('get_harga_diskon')
    stok_barang = serializers.SerializerMethodField('get_stok_barang')
    saldo = serializers.SerializerMethodField('get_saldo')

    def get_nomor_barang(self, value: Item):
        return value.barang.nomor

    def get_nama_barang(self, value: Item):
        return value.barang.nama

    def get_jenis(self, value: Item):
        return value.barang.jenis

    def get_satuan(self, value: Item):
        return value.barang.satuan

    def get_harga_diskon(self, value: Item):
        return value.harga - (value.harga * (value.diskon / 100))

    def get_stok_barang(self, value: Item):
        return value.barang.stok

    def get_saldo(self, value: Item):
        return value.barang.stok + value.quantity

    class Meta:
        model = Item
        fields = [
            'id',
            'pembelian',
            'barang',
            'harga',
            'diskon',
            'harga_diskon',
            'quantity',
            'total',
            'nomor_barang',
            'nama_barang',
            'jenis',
            'satuan',
            'stok_barang',
            'saldo',
        ]

        read_only_fields = [
            'harga_diskon',
            'total',
            'pembelian',
            'nomor_barang',
            'nama_barang',
            'jenis',
            'satuan',
            'stok_barang',
            'saldo',
        ]


class PembayaranSerializer(serializers.ModelSerializer):
    nomor_pembelian = serializers.SerializerMethodField('get_nomor_pembelian')

    def get_nomor_pembelian(self, value: Pembayaran):
        return value.pembelian.nomor

    class Meta:
        model = Pembayaran
        fields = [
            'id',
            'nomor',
            'tanggal',
            'pembelian',
            'total',
            'ppn',
            'diskon',
            'dibayar',
            'sisa',
            'kembali',
            'metode',
            'lunas',
            'tempo',
            'jatuh_tempo',
            'nomor_pembelian',
        ]

        read_only_fields = [
            'nomor',
            'tanggal',
            'pembelian',
            'total',
            'sisa',
            'kembali',
            'metode',
            'lunas',
            'jatuh_tempo',
            'nomor_pembelian',
        ]


class HutangSerializer(serializers.ModelSerializer):
    nomor_pembelian = serializers.SerializerMethodField('get_nomor_pembelian')
    nomor_pembayaran = serializers.SerializerMethodField('get_nomor_pembayaran')
    jumlah_hutang = serializers.SerializerMethodField('get_jumlah_hutang')

    def get_nomor_pembelian(self, value: Hutang):
        return value.pembayaran.pembelian.nomor

    def get_nomor_pembayaran(self, value: Hutang):
        return value.pembayaran.nomor

    def get_jumlah_hutang(self, value: Hutang):
        return value.pembayaran.sisa

    class Meta:
        model = Hutang
        fields = [
            'id',
            'nomor',
            'pembayaran',
            'tanggal',
            'dibayar',
            'sisa',
            'keterangan',
            'nomor_pembelian',
            'nomor_pembayaran',
            'jumlah_hutang',
        ]

        read_only_fields = [
            'nomor',
            'pembayaran',
            'sisa',
            'nomor_pembelian',
            'nomor_pembayaran',
            'jumlah_hutang',
        ]


class ReturPembelianSerializer(serializers.ModelSerializer):
    nama_supplier = serializers.SerializerMethodField('get_nama_supplier')
    nomor_supplier = serializers.SerializerMethodField('get_nomor_supplier')
    status_pembayaran = serializers.SerializerMethodField('get_status_pembayaran')
    jumlah_barang = serializers.SerializerMethodField('get_jumlah_barang')
    metode_pembayaran = serializers.SerializerMethodField('get_metode_pembayaran')
    nomor_pembelian = serializers.SerializerMethodField('get_nomor_pembelian')

    def get_nama_supplier(self, value: ReturPembelian):
        return value.pembelian.supplier.nama

    def get_nomor_supplier(self, value: ReturPembelian):
        return value.pembelian.supplier.nomor

    def get_status_pembayaran(self, value: ReturPembelian):
        if value.pembelian.pembayaran_pembelian.lunas:
            return 'Lunas'
        return 'Belum Lunas'

    def get_jumlah_barang(self, value: ReturPembelian):
        return value.pembelian.daftar_item_pembelian.all().count()

    def get_metode_pembayaran(self, value: ReturPembelian):
        return value.pembelian.pembayaran_pembelian.metode

    def get_nomor_pembelian(self, value: ReturPembelian):
        return value.pembelian.nomor

    class Meta:
        model = ReturPembelian
        fields = [
            'id',
            'nomor',
            'pembelian',
            'tanggal',
            'is_draft',
            'user',
            'nama_supplier',
            'nomor_supplier',
            'status_pembayaran',
            'jumlah_barang',
            'metode_pembayaran',
            'nomor_pembelian',
        ]

        read_only_fields = [
            'nomor',
            'pembelian',
            'is_draft',
            'user',
            'nama_supplier',
            'nomor_supplier',
            'status_pembayaran',
            'jumlah_barang',
            'metode_pembayaran',
            'nomor_pembelian',
        ]


class ReturItemPembelianSerializer(serializers.ModelSerializer):
    harga_item = serializers.SerializerMethodField('get_harga_item')
    diskon_item = serializers.SerializerMethodField('get_diskon_item')
    quantity_item = serializers.SerializerMethodField('get_quantity_item')
    nomor_barang = serializers.SerializerMethodField('get_nomor_barang')
    nama_barang = serializers.SerializerMethodField('get_nama_barang')
    jenis_barang = serializers.SerializerMethodField('get_jenis_barang')
    satuan_barang = serializers.SerializerMethodField('get_satuan_barang')
    is_quantity_valid = serializers.SerializerMethodField('get_is_quantity_valid')

    def get_harga_item(self, value: ReturItemPembelian):
        return value.item.harga

    def get_diskon_item(self, value: ReturItemPembelian):
        return value.item.diskon

    def get_quantity_item(self, value: ReturItemPembelian):
        return value.item.quantity

    def get_nomor_barang(self, value: ReturItemPembelian):
        return value.barang.nomor

    def get_nama_barang(self, value: ReturItemPembelian):
        return value.barang.nama

    def get_jenis_barang(self, value: ReturItemPembelian):
        return value.barang.jenis

    def get_satuan_barang(self, value: ReturItemPembelian):
        return value.barang.satuan

    def get_is_quantity_valid(self, value: ReturItemPembelian):
        return value.item.quantity > value.quantity

    class Meta:
        model = ReturItemPembelian
        fields = [
            'id',
            'retur_pembelian',
            'barang',
            'item',
            'quantity',
            'alasan',
            'harga_item',
            'diskon_item',
            'quantity_item',
            'nomor_barang',
            'nama_barang',
            'jenis_barang',
            'satuan_barang',
            'is_quantity_valid',
        ]
        read_only_fields = [
            'retur_pembelian',
            'barang',
            'item',
            'harga_item',
            'diskon_item',
            'quantity_item',
            'nomor_barang',
            'nama_barang',
            'jenis_barang',
            'satuan_barang',
            'is_quantity_valid',
        ]
