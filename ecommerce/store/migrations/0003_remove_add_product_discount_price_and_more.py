# Generated by Django 5.1 on 2024-08-23 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_add_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='add_product',
            name='discount_price',
        ),
        migrations.AlterField(
            model_name='add_product',
            name='image1',
            field=models.ImageField(upload_to='admin_img/'),
        ),
        migrations.AlterField(
            model_name='add_product',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='admin_img/'),
        ),
        migrations.AlterField(
            model_name='add_product',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to='admin_img/'),
        ),
    ]
