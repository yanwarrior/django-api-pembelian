# Generated by Django 5.0 on 2024-01-28 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pembelian', '0003_alter_returpembelian_tanggal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returpembelian',
            name='tanggal',
            field=models.DateField(auto_created=True),
        ),
    ]
