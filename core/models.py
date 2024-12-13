from django.db import models
import uuid

def product_audio_upload_to(instance, filename):
    # Create a dynamic path based on instance's `call_sid` and `id`
    return f'audio/{instance.call_sid}/{uuid.uuid4()}/{filename}'

class Product(models.Model):
    call_sid = models.CharField(max_length=34, unique=False)

    # Audio File
    audio_url = models.FileField(upload_to=product_audio_upload_to, blank=False, null=False)

    # Transcribed Text Fields
    audio_transcription = models.TextField(blank=True, null=True)

    # Extracted Fields via NER
    extracted_product_name = models.CharField(max_length=255, blank=True, null=True)
    extracted_description = models.TextField(blank=True, null=True)
    extracted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    extracted_location = models.CharField(max_length=255, blank=True, null=True)

    # Status Flags
    pending_transcription = models.BooleanField(default=True)
    pending_ner = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product {self.id} - {'Processed' if self.processed else 'Pending'}"
    
    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
