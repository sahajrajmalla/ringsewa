from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'call_sid',
        'audio_url',
        'extracted_product_name',
        'extracted_description',
        'extracted_price',
        'pending_transcription',
        'pending_ner',
        'created_at',
    )
    list_filter = ('pending_transcription', 'pending_ner', 'created_at')
    search_fields = ('extracted_product_name', 'extracted_description')
