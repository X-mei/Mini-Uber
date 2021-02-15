# Generated by Django 3.1.5 on 2021-02-07 08:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0002_ride'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='driver_rides', to=settings.AUTH_USER_MODEL),
        ),
    ]
