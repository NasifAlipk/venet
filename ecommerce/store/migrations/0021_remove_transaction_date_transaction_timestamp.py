# Generated by Django 5.1 on 2024-10-13 16:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_order_razorpay_order_id_alter_order_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='date',
        ),
        migrations.AddField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]