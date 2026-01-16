from django.urls import path
from .views import (
    product_views,
    admin_views,
    motoboy_view,
    source_views,
    marketing_views,
    auth_views,
    user_views,
)
from .views import order_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("auth/register/", auth_views.RegisterView.as_view(), name="auth-register"),
    path(
        "auth/admin/register/",
        auth_views.AdminRegisterView.as_view(),
        name="auth-admin-register",
    ),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "auth/admin/login/",
        auth_views.AdminLoginView.as_view(),
        name="auth-admin-login",
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", user_views.GetMeView.as_view(), name="auth-me"),
    path("auth/user/update/<int:id>/", user_views.UserUpdateView.as_view(), name="auth-user-update"),
    path("auth/user/delete/<int:id>/", user_views.DeleteAccountView.as_view(), name="auth-user-delete"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "get-products/",
        product_views.ProductListView.as_view(),
        name="product-list-create",
    ),
    path(
        "my-notifications/",
        user_views.UserNotificationsView.as_view(),
        name="user-notifications"
    ), 
    path(
        "my-orders/",
        user_views.MyOrdersView.as_view(),
        name="my-orders"
    ),
    path("admin/product/", product_views.create_product, name="product-create"),
    path(
        "admin/product/<int:id>/",
        product_views.update_product,
        name="product-update",
    ),
    path(
        "products/<int:id>/",
        product_views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "search-products/", 
        product_views.SearchproductView.as_view(), 
        name="search-products"
    ),
    path(
        "admin/motoboys/",
        motoboy_view.MotoboyListCreateView.as_view(),
        name="motoboy-list-create",
    ),
    path(
        "admin/update-motoboy/<int:id>",
        motoboy_view.MotoboyUpdate.as_view(),
        name="Update-Motoboy",
    ),
    path(
        "admin/delete-motoboy/<int:id>/",
        motoboy_view.MotoboyDelete.as_view(),
        name="Delete-Motoboy",
    ),
    path("admin/stats/weekly/", admin_views.AdminStatsView.as_view(), name="admin-stats"),
    path("admin/stats/annual/", admin_views.AdminAnnualStatsView.as_view(), name="admin-annual-stats"),
    path("admin/stats/monthly/", admin_views.AdminMonthlyStatsView.as_view(), name="admin-monthly-stats"),
    path("admin/stats/daily/", admin_views.AdminDailyStatsView.as_view(), name="admin-daily-stats"),
    path(
        "admin/sources/",
        source_views.GetReferralStatsView.as_view(),
        name="admin-get-sources",
    ),
    path(
        "sources/", source_views.PostReferralStatsView.as_view(), name="Create-Source"
    ),
    path(
        "admin/users/", admin_views.AdminUserListView.as_view(), name="admin-user-list"
    ),
    path(
        "admin/marketing/create/",
        marketing_views.create_marketing,
        name="marketing-create",
    ),
    path(
        "admin/marketing/<int:id>/add-products/",
        marketing_views.add_products_to_marketing,
        name="add-products-to-marketing",
    ),
    path(
        "admin/marketing/",
        marketing_views.active_marketing,
        name="marketing-list",
    ),
    path(
        "admin/marketing/<int:id>/",
        marketing_views.MarketingDetailView.as_view(),
        name="marketing-detail",
    ),
    path(
        "admin/marketing/<int:id>/delete/",
        marketing_views.MarketingDeleteView.as_view(),
        name="marketing-delete",
    ),
    path(
        "admin/create-role/",
        admin_views.AdminCreateRole.as_view(),
        name="admin-create-role",
    ),
    path("admin/create-superadmin/", auth_views.SuperAdminRegisterView.as_view(), name="admin-create-superadmin"),

    # orders / checkout
    path("checkout/", order_views.CheckoutView.as_view(), name="checkout"),
    path(
        "orders/<int:id>/", order_views.OrderDetailView.as_view(), name="order-detail"
    ),
    path(
        "admin/order/<int:id>/advance/",
        order_views.AdvanceStatusView.as_view(),
        name="accept-order",
    ),
    path(
        "admin/order/<int:id>/reject/",
        order_views.RejectOrderView.as_view(),
        name="reject-order",
    ),
    path("admin/orders/", order_views.OrderList.as_view(), name="list-order"),
    path("my-orders/", order_views.MyOrdersView.as_view(), name="my-orders"),
    path(
        "orders/<int:order_id>/send-to-courier/",
        motoboy_view.send_order_to_courier,
        name="send_order_to_courier",
    ),
]
