def generate_nomor(prefix, queryset):
    count = str(queryset.last().id + 1)
    return f'{prefix}{count.zfill(4)}'