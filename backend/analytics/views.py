from datetime import date, datetime

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.queries import (
    fetch_kpis,
    fetch_revenue_trends,
    fetch_rfm_segments,
    fetch_top_products,
)


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
            return Response({"error": "date_from must be <= date_to"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"kpis:{date_from}:{date_to}"
        cached = cache.get(cache_key)
        if cached:
            cached["cache"] = {"hit": True, "key": cache_key, "ttl_seconds": 300}
            return Response(cached, status=status.HTTP_200_OK)

        data = fetch_kpis(date_from, date_to)
        cache.set(cache_key, data, timeout=300)
        data["cache"] = {"hit": False, "key": cache_key, "ttl_seconds": 300}
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

        if date_from > date_to:
            return Response({"error": "date_from must be <= date_to"}, status=status.HTTP_400_BAD_REQUEST)

        granularity = (request.GET.get("granularity") or "daily").lower()

        cache_key = f"revenue_trends:{granularity}:{date_from}:{date_to}"
        cached = cache.get(cache_key)
        if cached:
            cached["cache"] = {"hit": True, "key": cache_key, "ttl_seconds": 300}
            return Response(cached, status=status.HTTP_200_OK)

        try:
            points = fetch_revenue_trends(date_from, date_to, granularity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "granularity": granularity,
            "date_from": str(date_from),
            "date_to": str(date_to),
            "points": points,
        }
        cache.set(cache_key, payload, timeout=300)
        payload["cache"] = {"hit": False, "key": cache_key, "ttl_seconds": 300}
        return Response(payload, status=status.HTTP_200_OK)


class CustomerSegmentsView(APIView):
    """
    GET /api/v1/customers/segments/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    Returns aggregated RFM segments counts.
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

        if date_from > date_to:
            return Response({"error": "date_from must be <= date_to"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"rfm_segments:{date_from}:{date_to}"
        cached = cache.get(cache_key)
        if cached:
            cached["cache"] = {"hit": True, "key": cache_key, "ttl_seconds": 600}
            return Response(cached, status=status.HTTP_200_OK)

        data = fetch_rfm_segments(date_from, date_to)
        cache.set(cache_key, data, timeout=600)
        data["cache"] = {"hit": False, "key": cache_key, "ttl_seconds": 600}
        return Response(data, status=status.HTTP_200_OK)


class TopProductsView(APIView):
    """
    GET /api/v1/products/top-sellers/?metric=revenue|quantity&limit=10&date_from=...&date_to=...
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

        if date_from > date_to:
            return Response({"error": "date_from must be <= date_to"}, status=status.HTTP_400_BAD_REQUEST)

        metric = (request.GET.get("metric") or "revenue").lower()

        limit_raw = request.GET.get("limit", "10")
        try:
            limit = int(limit_raw)
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"top_products:{metric}:{limit}:{date_from}:{date_to}"
        cached = cache.get(cache_key)
        if cached:
            cached["cache"] = {"hit": True, "key": cache_key, "ttl_seconds": 300}
            return Response(cached, status=status.HTTP_200_OK)

        try:
            data = fetch_top_products(date_from, date_to, metric, limit)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        cache.set(cache_key, data, timeout=300)
        data["cache"] = {"hit": False, "key": cache_key, "ttl_seconds": 300}
        return Response(data, status=status.HTTP_200_OK)
