# Generated by Django 5.1 on 2024-10-18 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_order_applied_coupon_order_discount_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='applied_coupon',
        ),
        migrations.RemoveField(
            model_name='order',
            name='discount_amount',
        ),
    ]
