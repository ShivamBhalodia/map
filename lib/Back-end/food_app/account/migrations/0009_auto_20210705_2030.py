# Generated by Django 3.1.7 on 2021-07-05 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20210705_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_order_history',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
