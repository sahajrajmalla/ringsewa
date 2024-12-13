from django.db import models

class Product(models.Model):
    call_sid = models.CharField(max_length=34, unique=False)

    # Audio File
    audio_url = models.FileField(upload_to=f'audio/{call_sid}/{id}/', blank=False, null=False)

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
