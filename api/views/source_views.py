from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from ..models import source_model


class GetReferralStatsView(APIView):
    def get(self, request):
        data = (
            source_model.UserReferral.objects.values("source")
            .annotate(total=Count("source"))
            .order_by("-total")
        )
        return Response(data)


class PostReferralStatsView(APIView):
    def post(self, request):
        source = request.data.get("source")
        if source not in dict(
            source_model.UserReferral._meta.get_field("source").choices
        ):
            return Response({"error": "Invalid source"}, status=400)
        source_model.UserReferral.objects.create(source=source)
        return Response({"message": "Saved successfully"}, status=201)
