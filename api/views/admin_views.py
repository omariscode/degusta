from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta

from ..models import order_model, user_model, motoboy_model, role_model
from ..serializers import UserSerializer, CourierSerializer, RoleSerializer


def calculate_trend(current, previous):
    if not previous:
        return 0
    return ((current - previous) / previous) * 100 if previous else 0


class AdminStatsView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        # Time ranges
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        thirty_days_ago = today - timedelta(days=30)
        previous_thirty_days = thirty_days_ago - timedelta(days=30)

        completed_orders = order_model.Order.objects.filter(
            status__in=["paid", "on_the_way", "delivered"]
        )

        # Card 1: Total Sales with 30-day trend
        current_month_sales = (
            completed_orders.filter(created_at__gte=thirty_days_ago).aggregate(
                total=Sum("total")
            )["total"]
            or 0
        )

        previous_month_sales = (
            completed_orders.filter(
                created_at__range=(previous_thirty_days, thirty_days_ago)
            ).aggregate(total=Sum("total"))["total"]
            or 0
        )

        sales_trend = calculate_trend(current_month_sales, previous_month_sales)

        # Card 2: Total Customers with trend
        current_customers = user_model.User.objects.filter(
            data_joined__gte=thirty_days_ago
        ).count()
        previous_customers = user_model.User.objects.filter(
            data_joined__range=(previous_thirty_days, thirty_days_ago)
        ).count()
        customer_trend = calculate_trend(current_customers, previous_customers)

        # Card 3: Today's Orders
        todays_orders = completed_orders.filter(created_at__gte=today).count()
        yesterday_orders = completed_orders.filter(
            created_at__range=(yesterday, today)
        ).count()
        orders_trend = calculate_trend(todays_orders, yesterday_orders)

        # Card 4: 30-day Order Completion Rate
        total_30day_orders = order_model.Order.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        completed_30day_orders = completed_orders.filter(
            created_at__gte=thirty_days_ago
        ).count()
        completion_rate = (
            (completed_30day_orders / total_30day_orders * 100)
            if total_30day_orders
            else 0
        )

        # Daily sales for chart (15 days)
        fifteen_days_ago = today - timedelta(days=7)
        daily_sales = (
            completed_orders.filter(created_at__gte=fifteen_days_ago)
            .annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(total=Sum("total"), count=Count("id"))
            .order_by("day")
        )

        # Format response
        return Response(
            {
                "cards": {
                    "total_sales": {
                        "value": float(current_month_sales),
                        "trend": round(sales_trend, 1),
                        "trend_type": "up" if sales_trend > 0 else "down",
                        "period": "30 dias",
                    },
                    "customers": {
                        "value": current_customers,
                        "trend": round(customer_trend, 1),
                        "trend_type": "up" if customer_trend > 0 else "down",
                        "period": "30 dias",
                    },
                    "todays_orders": {
                        "value": todays_orders,
                        "trend": round(orders_trend, 1),
                        "trend_type": "up" if orders_trend > 0 else "down",
                        "period": "24h",
                    },
                    "completion_rate": {
                        "value": round(completion_rate, 1),
                        "period": "30 dias",
                    },
                },
                "daily_sales": [
                    {
                        "day": item["day"].strftime("%d"),
                        "total": float(item["total"]),
                        "count": item["count"],
                    }
                    for item in daily_sales
                ],
            }
        )


class AdminUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = user_model.User.objects.all().order_by("-id")
    serializer_class = UserSerializer

class AdminCourierListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = motoboy_model.Courier.objects.all().order_by("-id")
    serializer_class = CourierSerializer


class AdminCourierCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CourierSerializer
    queryset = motoboy_model.Courier.objects.all()

class AdminCreateRole(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RoleSerializer
    queryset = role_model.Role.objects.all()