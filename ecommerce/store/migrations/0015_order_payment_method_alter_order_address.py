# Generated by Django 5.1 on 2024-10-02 05:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_rename_add_product_wishlistitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('COD', 'Cash on Delivery'), ('Razorpay', 'Razorpay')], default='COD', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.address'),
        ),
    ]
