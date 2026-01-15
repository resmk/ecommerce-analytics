from django.urls import path
from analytics.views import KPIView, RevenueTrendsView, CustomerSegmentsView

urlpatterns = [
    path("kpis/", KPIView.as_view(), name="kpis"),
    path("revenue/trends/", RevenueTrendsView.as_view(), name="revenue-trends"),
    path("customers/segments/", CustomerSegmentsView.as_view(), name="customer-segments"),
]
