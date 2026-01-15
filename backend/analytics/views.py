from datetime import date, datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from analytics.queries import fetch_kpis


def parse_date(value: str, fallback: date) -> date:
    if not value:
        return fallback
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")


class KPIView(APIView):
    """
    GET /api/v1/kpis/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    """
    authentication_classes = []  # we'll add JWT later
    permission_classes = []      # we'll add auth later

    def get(self, request):
        today = date.today()
        date_from_default = today.replace(day=1)  # start of current month
        date_to_default = today

        try:
            date_from = parse_date(request.GET.get("date_from"), date_from_default)
            date_to = parse_date(request.GET.get("date_to"), date_to_default)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if date_from > date_to:
            return Response(
                {"error": "date_from must be <= date_to"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = fetch_kpis(date_from, date_to)
        return Response(data, status=status.HTTP_200_OK)
