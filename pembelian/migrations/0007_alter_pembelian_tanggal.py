# Generated by Django 5.0 on 2024-02-12 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pembelian', '0006_alter_pembelian_tanggal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pembelian',
            name='tanggal',
            field=models.DateTimeField(auto_created=True),
        ),
    ]
