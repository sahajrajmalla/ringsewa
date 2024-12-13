from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .utils import extract_and_save
from django.conf import settings

@receiver(post_save, sender=Product)
def handle_product_creation(sender, instance, created, **kwargs):
    if created:
        # Trigger transcription task
        
        print(f"New Product created using Signals: {instance.call_sid}")
    
        extract_and_save(instance)
