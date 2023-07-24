# Generated by Django 4.2.2 on 2023-07-17 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_alter_order_order_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment_gateway_token',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=25, null=True, unique=True),
        ),
    ]