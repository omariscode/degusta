from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..utils.cloud import upload_to_cloudinary_marketing
from ..models import marketing_model, product_model
from ..serializers import MarketingSerializer
from rest_framework import permissions
from django.utils import timezone

@api_view(["POST"])
def create_marketing(request):
    if "cover" not in request.FILES:
        return Response(
            {"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        image_file = request.FILES["cover"]
        image_url = upload_to_cloudinary_marketing(image_file)

        data = request.data.copy()
        data["cover"] = image_url

        serializer = MarketingSerializer(data=data)

        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {
                    "message": "Marketing criado com sucesso!",
                    "marketing": MarketingSerializer(product).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def active_marketing(request):
    now = timezone.now()
    campaigns = marketing_model.Marketing.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )
    serializer = MarketingSerializer(campaigns, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def marketing_detail(request, id):
    campaign = get_object_or_404(marketing_model.Marketing, id=id)
    serializer = MarketingSerializer(campaign)
    return Response(serializer.data)

@api_view(["POST"])
def add_products_to_marketing(request, id):
    campaign = get_object_or_404(marketing_model.Marketing, id=id)
    product_ids = request.data.get("products", [])

    products = product_model.Product.objects.filter(id__in=product_ids)
    campaign.products.add(*products)

    return Response({"message": "Produtos adicionados com sucesso"})


class MarketingDeleteView(generics.DestroyAPIView):
    queryset = marketing_model.Marketing.objects.all()
    serializer_class = MarketingSerializer    
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'