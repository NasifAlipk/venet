# Generated by Django 5.1 on 2024-11-24 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_orderitem_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('street_address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('postcode', models.CharField(max_length=20)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order_address', to='store.order')),
            ],
        ),
    ]
