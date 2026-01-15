from datetime import date, datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from analytics.queries import fetch_kpis, fetch_revenue_trends


def parse_date(value: str | None, fallback: date) -> date:
    """
    Parse YYYY-MM-DD into a date. If value is empty/None, return fallback.
    """
    if not value:
        return fallback
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.") from e


class KPIView(APIView):
    """
    GET /api/v1/kpis/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    """
    authentication_classes = []  # add JWT later
    permission_classes = []      # add auth later

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


class RevenueTrendsView(APIView):
    """
    GET /api/v1/revenue/trends/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD&granularity=daily|weekly|monthly
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        today = date.today()
        date_from_default = today.replace(day=1)
        date_to_default = today

        try:
            date_from = parse_date(request.GET.get("date_from"), date_from_default)
            date_to = parse_date(request.GET.get("date_to"), date_to_default)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        granularity = (request.GET.get("granularity") or "daily").lower()

        if date_from > date_to:
            return Response(
                {"error": "date_from must be <= date_to"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            points = fetch_revenue_trends(date_from, date_to, granularity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "granularity": granularity,
                "date_from": str(date_from),
                "date_to": str(date_to),
                "points": points,
            },
            status=status.HTTP_200_OK,
        )
