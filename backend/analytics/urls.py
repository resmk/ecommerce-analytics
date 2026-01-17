from django.urls import path
from analytics.views import (
    KPIView,
    RevenueTrendsView,
    CustomerSegmentsView,
    TopProductsView,
    OrdersListView,
)

urlpatterns = [
    path("kpis/", KPIView.as_view(), name="kpis"),
    path("revenue/trends/", RevenueTrendsView.as_view(), name="revenue-trends"),
    path("customers/segments/", CustomerSegmentsView.as_view(), name="customer-segments"),
    path("products/top-sellers/", TopProductsView.as_view(), name="top-products"),
    path("orders/", OrdersListView.as_view(), name="orders"),
]
