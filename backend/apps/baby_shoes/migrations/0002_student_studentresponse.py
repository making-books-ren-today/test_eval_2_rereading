# Generated by Django 2.2.3 on 2019-07-23 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baby_shoes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_response', to='baby_shoes.Context')),
            ],
        ),
        migrations.CreateModel(
            name='StudentResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.IntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='baby_shoes.Student')),
            ],
        ),
    ]
