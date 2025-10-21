from rest_framework import generics, permissions
from ..models import product_model
from ..serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = product_model.Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = product_model.Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
