# Generated by Django 5.1 on 2024-10-02 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_remove_order_payment_method_alter_order_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('minimum_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_percentage', models.PositiveIntegerField()),
                ('expiry_date', models.DateField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive', max_length=8)),
            ],
        ),
    ]