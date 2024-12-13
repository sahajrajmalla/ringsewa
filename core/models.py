from django.db import models

class Product(models.Model):
    call_sid = models.CharField(max_length=34, unique=True)  # Unique identifier from the call

    # Audio Files
    product_name_audio = models.FileField(upload_to='audio/product_name/')
    description_audio = models.FileField(upload_to='audio/description/')
    price_audio = models.FileField(upload_to='audio/price/')
    location_audio = models.FileField(upload_to='audio/location/', blank=True, null=True)  # Optional

    # Transcribed Text Fields
    product_name_text = models.TextField(blank=True, null=True)
    description_text = models.TextField(blank=True, null=True)
    price_text = models.TextField(blank=True, null=True)
    location_text = models.TextField(blank=True, null=True)  # Optional

    # Extracted Fields via NER
    extracted_product_name = models.CharField(max_length=255, blank=True, null=True)
    extracted_description = models.TextField(blank=True, null=True)
    extracted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    extracted_location = models.CharField(max_length=255, blank=True, null=True)  # Optional

    # Status Flags
    pending_transcription = models.BooleanField(default=True)
    pending_ner = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product {self.id} - {'Processed' if self.processed else 'Pending'}"
