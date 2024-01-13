def generate_nomor(prefix, queryset):
    id = 0
    if queryset.last():
        id = queryset.last().id

    count = str(id + 1)
    return f'{prefix}{count.zfill(4)}'