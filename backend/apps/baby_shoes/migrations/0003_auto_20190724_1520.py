# Generated by Django 2.2.3 on 2019-07-24 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baby_shoes', '0002_student_studentresponse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentresponse',
            name='response',
            field=models.TextField(),
        ),
    ]
