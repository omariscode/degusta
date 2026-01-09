from rest_framework import generics, permissions
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import product_model
from ..serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..utils.cloud import upload_to_cloudinary_product
from rest_framework import status


@api_view(["POST"])
def create_product(request):
    if "image" not in request.FILES:
        return Response(
            {"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        image_file = request.FILES["image"]
        image_url = upload_to_cloudinary_product(image_file)

        data = request.data.copy()
        data["image"] = image_url

        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {
                    "message": "Produto criado com sucesso!",
                    "project": ProductSerializer(product).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["PUT"])
def update_product(request, id):
    try:
        product = product_model.Product.objects.get(id=id)
    except product_model.Product.DoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data.copy()

    if "image" in request.FILES:
        image_file = request.FILES["image"]
        image_url = upload_to_cloudinary_product(image_file)
        data["image"] = image_url

    serializer = ProductSerializer(product, data=data, partial=True)

    if serializer.is_valid():
        updated_product = serializer.save()
        return Response(
            {
                "message": "Product updated successfully!",
                "product": ProductSerializer(updated_product).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(generics.ListAPIView):
    queryset = product_model.Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 5), name="dispatch")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"

    queryset = product_model.Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 5), name="dispatch")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class SearchproductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return product_model.Product.objects.filter(name__icontains=query)