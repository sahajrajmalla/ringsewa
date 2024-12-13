# Generated by Django 4.2 on 2024-12-13 13:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_product_call_sid_alter_product_location_audio"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="description_text",
            new_name="audio_transcription",
        ),
        migrations.RemoveField(model_name="product", name="description_audio",),
        migrations.RemoveField(model_name="product", name="location_audio",),
        migrations.RemoveField(model_name="product", name="location_text",),
        migrations.RemoveField(model_name="product", name="price_audio",),
        migrations.RemoveField(model_name="product", name="price_text",),
        migrations.RemoveField(model_name="product", name="product_name_audio",),
        migrations.RemoveField(model_name="product", name="product_name_text",),
        migrations.AddField(
            model_name="product",
            name="audio_url",
            field=models.FileField(
                default=django.utils.timezone.now,
                upload_to="audio/<django.db.models.fields.CharField>/<built-in function id>/",
            ),
            preserve_default=False,
        ),
    ]
