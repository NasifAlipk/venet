# Generated by Django 5.1 on 2024-09-11 04:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='apartment',
        ),
        migrations.RemoveField(
            model_name='address',
            name='company_name',
        ),
        migrations.RemoveField(
            model_name='address',
            name='country',
        ),
    ]
