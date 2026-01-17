from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from etl.models import ETLRun
from etl.serializers import ETLRunSerializer
from etl.tasks import load_csv_orders_task


class ETLStatusView(APIView):
    """
    GET /api/v1/etl/status/?limit=20
    Public status endpoint (you can later protect if you want).
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        limit_raw = request.GET.get("limit", "20")
        try:
            limit = max(1, min(int(limit_raw), 100))
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        runs = ETLRun.objects.order_by("-run_id")[:limit]
        data = ETLRunSerializer(runs, many=True).data
        return Response({"count": len(data), "runs": data}, status=status.HTTP_200_OK)


class ETLTriggerView(APIView):
    """
    POST /api/v1/etl/trigger/
    Triggers ETL asynchronously via Celery (JWT required).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task = load_csv_orders_task.delay()
        return Response(
            {"message": "ETL triggered", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED,
        )
