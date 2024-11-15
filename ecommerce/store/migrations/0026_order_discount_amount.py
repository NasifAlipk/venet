# Generated by Django 5.1 on 2024-10-21 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_remove_order_applied_coupon_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
