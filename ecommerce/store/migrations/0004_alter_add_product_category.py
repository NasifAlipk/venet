# Generated by Django 5.1 on 2024-08-23 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_add_product_discount_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.category'),
        ),
    ]