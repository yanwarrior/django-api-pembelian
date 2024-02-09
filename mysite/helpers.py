def generate_nomor(prefix, queryset, counter=1):
    id = 0
    if queryset.last():
        id = queryset.last().id

    count = str(id + counter)
    return f'{prefix}{count.zfill(4)}'