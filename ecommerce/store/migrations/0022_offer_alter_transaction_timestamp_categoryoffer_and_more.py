# Generated by Django 5.1 on 2024-10-16 05:10

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_remove_transaction_date_transaction_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('discount_percentage', models.PositiveIntegerField()),
                ('offer_type', models.CharField(choices=[('product', 'Product'), ('category', 'Category')], max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')], default='inactive', max_length=10)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='CategoryOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='store.category')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_offers', to='store.offer')),
            ],
        ),
        migrations.CreateModel(
            name='ProductOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_offers', to='store.offer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='store.add_product')),
            ],
        ),
    ]
