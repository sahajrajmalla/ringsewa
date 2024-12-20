# Generated by Django 4.2 on 2024-12-13 12:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="call_sid",
            field=models.CharField(max_length=34),
        ),
        migrations.AlterField(
            model_name="product",
            name="location_audio",
            field=models.FileField(
                default=django.utils.timezone.now, upload_to="audio/location/"
            ),
            preserve_default=False,
        ),
    ]
