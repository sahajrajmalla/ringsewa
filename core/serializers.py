# core/serializers.py

from rest_framework import serializers
from .models import Product

class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Product with audio files.
    """
    audio_url = serializers.FileField(write_only=True)
    
    class Meta:
        model = Product
        fields = ['call_sid', 'audio_url']

class ProductRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving Product information (with transcribed text and extracted fields).
    """
    class Meta:
        model = Product
        fields = [
            'id',
            'call_sid',
            'audio_url',
            'audio_transcription',
            'extracted_product_name',
            'extracted_description',
            'extracted_price',
            'extracted_location',
            'created_at',
            'processed',
            'pending_transcription',
            'pending_ner',
        ]
        read_only_fields = ['id', 'created_at', 'processed']
