from django.urls import path
from analytics.views import KPIView

urlpatterns = [
    path("kpis/", KPIView.as_view(), name="kpis"),
]
