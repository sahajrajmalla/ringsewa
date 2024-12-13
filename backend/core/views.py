# core/views.py

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Product
from .serializers import ProductCreateSerializer, ProductRetrieveSerializer
from .utils import extract_and_save  # Assuming you have a utility function to handle transcription and NER

from rest_framework.permissions import AllowAny



class ProductCreateAPIView(generics.CreateAPIView):
    """
    API view to create a new Product instance with an audio file upload.
    """
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [AllowAny]  # Open to everyone
    authentication_classes = []  # No authentication required

    @swagger_auto_schema(
        operation_description="Create a new Product with an audio file upload. The audio file will be processed for transcription.",
        request_body=ProductCreateSerializer,
        responses={
            201: 'Product created successfully.',
            400: 'Bad Request - Invalid data.',
            500: 'Internal Server Error - Processing failed.',
        },
        operation_summary="Create a product with an audio file."
    )
    def create(self, request, *args, **kwargs):
        """
        Handle the creation of a Product with an audio file upload.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()

            # Here you can add processing, such as transcription or NER if needed
            # success = extract_and_save(product.call_sid)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    """
    API view to retrieve a single Product by its `call_sid`.
    """
    queryset = Product.objects.all()
    serializer_class = ProductRetrieveSerializer
    permission_classes = [permissions.AllowAny]  # Open to everyone
    authentication_classes = []  # No authentication required


    @swagger_auto_schema(
        operation_description="Retrieve details of a specific Product by its ID.",
        responses={
            200: ProductRetrieveSerializer(),  # Success response with product data
            404: 'Product Not Found',
        },
        tags=['Product'],
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a single product by its unique ID (call_sid).
        """
        return super().get(request, *args, **kwargs)


class ProductListAPIView(generics.ListAPIView):
    """
    API view to list all Product instances.
    """
    queryset = Product.objects.all()
    serializer_class = ProductRetrieveSerializer
    permission_classes = [permissions.AllowAny]  # Open to everyone
    authentication_classes = []  # No authentication required


    @swagger_auto_schema(
        operation_description="List all Products in the system.",
        responses={
            200: ProductRetrieveSerializer(many=True),  # List of products
        },
        tags=['Product'],
    )
    def get(self, request, *args, **kwargs):
        """
        List all products with basic information (name, price, etc.).
        """
        return super().get(request, *args, **kwargs)
