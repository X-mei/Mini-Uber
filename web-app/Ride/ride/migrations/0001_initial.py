# Generated by Django 3.1.5 on 2021-01-30 12:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('vehicle_type', models.CharField(max_length=30)),
                ('license_number', models.CharField(max_length=30)),
                ('n_passengers', models.IntegerField(validators=[django.core.validators.MaxValueValidator(50), django.core.validators.MinValueValidator(1)])),
                ('special_info', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=40, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_driver', models.BooleanField(default=False)),
                ('driver_license', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ride.vehicleinfo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]