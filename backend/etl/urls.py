from django.urls import path
from etl.views import ETLStatusView, ETLTriggerView

urlpatterns = [
    path("etl/status/", ETLStatusView.as_view(), name="etl-status"),
    path("etl/trigger/", ETLTriggerView.as_view(), name="etl-trigger"),
]
