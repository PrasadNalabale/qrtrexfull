# Generated by Django 5.1.7 on 2025-05-08 10:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0005_offers_payment_is_paid_payment_signature'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant', to=settings.AUTH_USER_MODEL),
        ),
    ]
