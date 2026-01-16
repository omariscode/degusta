from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
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

    @method_decorator(cache_page(60 * 10))
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
            data_joined__gte=thirty_days_ago, role__name=None
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


class AdminAnnualStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @method_decorator(cache_page(60 * 10))
    def get(self, request, format=None):
        now = timezone.now()
        current_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_year_start = current_year_start - timedelta(days=365)
        previous_year_end = current_year_start - timedelta(days=1)

        completed_orders = order_model.Order.objects.filter(
            status__in=["paid", "on_the_way", "delivered"]
        )

        # Total Sales current year vs previous year
        current_year_sales = (
            completed_orders.filter(created_at__gte=current_year_start).aggregate(
                total=Sum("total")
            )["total"] or 0
        )
        previous_year_sales = (
            completed_orders.filter(
                created_at__range=(previous_year_start, previous_year_end)
            ).aggregate(total=Sum("total"))["total"] or 0
        )
        sales_trend = calculate_trend(current_year_sales, previous_year_sales)

        # Customers current year vs previous year
        current_year_customers = user_model.User.objects.filter(
            data_joined__gte=current_year_start, role__name=None
        ).count()
        previous_year_customers = user_model.User.objects.filter(
            data_joined__range=(previous_year_start, previous_year_end)
        ).count()
        customer_trend = calculate_trend(current_year_customers, previous_year_customers)

        # Orders current year
        current_year_orders = completed_orders.filter(created_at__gte=current_year_start).count()

        # Completion rate current year
        total_year_orders = order_model.Order.objects.filter(
            created_at__gte=current_year_start
        ).count()
        completed_year_orders = completed_orders.filter(
            created_at__gte=current_year_start
        ).count()
        completion_rate = (
            (completed_year_orders / total_year_orders * 100) if total_year_orders else 0
        )

        # Monthly sales for chart (12 months)
        monthly_sales = (
            completed_orders.filter(created_at__gte=current_year_start)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("total"), count=Count("id"))
            .order_by("month")
        )

        return Response(
            {
                "cards": {
                    "total_sales": {
                        "value": float(current_year_sales),
                        "trend": round(sales_trend, 1),
                        "trend_type": "up" if sales_trend > 0 else "down",
                        "period": "ano atual",
                    },
                    "customers": {
                        "value": current_year_customers,
                        "trend": round(customer_trend, 1),
                        "trend_type": "up" if customer_trend > 0 else "down",
                        "period": "ano atual",
                    },
                    "year_orders": {
                        "value": current_year_orders,
                        "period": "ano atual",
                    },
                    "completion_rate": {
                        "value": round(completion_rate, 1),
                        "period": "ano atual",
                    },
                },
                "monthly_sales": [
                    {
                        "month": item["month"].strftime("%m"),
                        "total": float(item["total"]),
                        "count": item["count"],
                    }
                    for item in monthly_sales
                ],
            }
        )


class AdminMonthlyStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @method_decorator(cache_page(60 * 10))
    def get(self, request, format=None):
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)

        completed_orders = order_model.Order.objects.filter(
            status__in=["paid", "on_the_way", "delivered"]
        )

        # Total Sales current month vs previous month
        current_month_sales = (
            completed_orders.filter(created_at__gte=current_month_start).aggregate(
                total=Sum("total")
            )["total"] or 0
        )
        previous_month_sales = (
            completed_orders.filter(
                created_at__range=(previous_month_start, previous_month_end)
            ).aggregate(total=Sum("total"))["total"] or 0
        )
        sales_trend = calculate_trend(current_month_sales, previous_month_sales)

        # Customers current month vs previous month
        current_month_customers = user_model.User.objects.filter(
            data_joined__gte=current_month_start, role__name=None
        ).count()
        previous_month_customers = user_model.User.objects.filter(
            data_joined__range=(previous_month_start, previous_month_end)
        ).count()
        customer_trend = calculate_trend(current_month_customers, previous_month_customers)

        # Orders current month
        current_month_orders = completed_orders.filter(created_at__gte=current_month_start).count()

        # Completion rate current month
        total_month_orders = order_model.Order.objects.filter(
            created_at__gte=current_month_start
        ).count()
        completed_month_orders = completed_orders.filter(
            created_at__gte=current_month_start
        ).count()
        completion_rate = (
            (completed_month_orders / total_month_orders * 100) if total_month_orders else 0
        )

        # Daily sales for chart (current month)
        daily_sales = (
            completed_orders.filter(created_at__gte=current_month_start)
            .annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(total=Sum("total"), count=Count("id"))
            .order_by("day")
        )

        return Response(
            {
                "cards": {
                    "total_sales": {
                        "value": float(current_month_sales),
                        "trend": round(sales_trend, 1),
                        "trend_type": "up" if sales_trend > 0 else "down",
                        "period": "mês atual",
                    },
                    "customers": {
                        "value": current_month_customers,
                        "trend": round(customer_trend, 1),
                        "trend_type": "up" if customer_trend > 0 else "down",
                        "period": "mês atual",
                    },
                    "month_orders": {
                        "value": current_month_orders,
                        "period": "mês atual",
                    },
                    "completion_rate": {
                        "value": round(completion_rate, 1),
                        "period": "mês atual",
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


class AdminDailyStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @method_decorator(cache_page(60 * 10))
    def get(self, request, format=None):
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        completed_orders = order_model.Order.objects.filter(
            status__in=["paid", "on_the_way", "delivered"]
        )

        # Total Sales today vs yesterday
        today_sales = (
            completed_orders.filter(created_at__gte=today).aggregate(
                total=Sum("total")
            )["total"] or 0
        )
        yesterday_sales = (
            completed_orders.filter(
                created_at__range=(yesterday, today)
            ).aggregate(total=Sum("total"))["total"] or 0
        )
        sales_trend = calculate_trend(today_sales, yesterday_sales)

        # Customers today vs yesterday
        today_customers = user_model.User.objects.filter(
            data_joined__gte=today, role__name=None
        ).count()
        yesterday_customers = user_model.User.objects.filter(
            data_joined__range=(yesterday, today)
        ).count()
        customer_trend = calculate_trend(today_customers, yesterday_customers)

        # Orders today
        today_orders = completed_orders.filter(created_at__gte=today).count()

        # Completion rate today
        total_today_orders = order_model.Order.objects.filter(
            created_at__gte=today
        ).count()
        completed_today_orders = completed_orders.filter(
            created_at__gte=today
        ).count()
        completion_rate = (
            (completed_today_orders / total_today_orders * 100) if total_today_orders else 0
        )

        # Hourly sales for today (if needed, but for now, just the cards)
        # Since it's daily, perhaps no chart, or hourly if possible

        return Response(
            {
                "cards": {
                    "total_sales": {
                        "value": float(today_sales),
                        "trend": round(sales_trend, 1),
                        "trend_type": "up" if sales_trend > 0 else "down",
                        "period": "hoje",
                    },
                    "customers": {
                        "value": today_customers,
                        "trend": round(customer_trend, 1),
                        "trend_type": "up" if customer_trend > 0 else "down",
                        "period": "hoje",
                    },
                    "today_orders": {
                        "value": today_orders,
                        "period": "hoje",
                    },
                    "completion_rate": {
                        "value": round(completion_rate, 1),
                        "period": "hoje",
                    },
                },
            }
        )