# Generated by Django 3.1.7 on 2021-06-25 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phoneotp',
            name='phone',
        ),
        migrations.AddField(
            model_name='phoneotp',
            name='username',
            field=models.CharField(default='', max_length=17, unique=True),
        ),
    ]
