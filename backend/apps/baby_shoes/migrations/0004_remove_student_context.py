# Generated by Django 2.2.3 on 2019-07-24 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baby_shoes', '0003_auto_20190724_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='context',
        ),
    ]