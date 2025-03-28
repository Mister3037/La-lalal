# Generated by Django 5.1.6 on 2025-02-20 16:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='RatingDriver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_type', models.IntegerField()),
                ('car_count', models.IntegerField(default=1)),
                ('height', models.CharField(blank=True, max_length=30, null=True)),
                ('length', models.CharField(blank=True, max_length=30, null=True)),
                ('distance', models.CharField(max_length=50)),
                ('load_type', models.CharField(default=True, max_length=100)),
                ('weight', models.CharField(blank=True, max_length=30, null=True)),
                ('width', models.CharField(blank=True, max_length=30, null=True)),
                ('load_time', models.CharField(max_length=100)),
                ('comment', models.CharField(blank=True, max_length=500, null=True)),
                ('order_status', models.CharField(choices=[('faol', 'faol'), ('olingan', 'olingan'), ('tugatilgan', 'tugatilgan')], default='faol', max_length=50)),
                ('is_finished', models.CharField(choices=[("yo'lda", "yo'lda"), ('yakunladi', 'yakunladi')], default="yo'lda", max_length=50)),
                ('price', models.CharField(max_length=100)),
                ('city_index', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14)])),
                ('views', models.BigIntegerField(blank=True, null=True)),
                ('address', models.ManyToManyField(to='customers.address')),
            ],
        ),
    ]
