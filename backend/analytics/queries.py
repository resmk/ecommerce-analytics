from datetime import date
from django.db import connection


def fetch_kpis(date_from: date, date_to: date) -> dict:
    """
    Returns basic KPI metrics for orders between date_from and date_to (inclusive).
    """
    sql = """
        SELECT
            COALESCE(SUM(order_amount), 0) AS total_revenue,
            COUNT(*) AS total_orders,
            COUNT(DISTINCT customer_key) AS unique_customers,
            COALESCE(AVG(order_amount), 0) AS avg_order_value
        FROM fact_orders
        WHERE created_at::date BETWEEN %s AND %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [date_from, date_to])
        row = cursor.fetchone()

    return {
        "total_revenue": float(row[0]),
        "total_orders": int(row[1]),
        "unique_customers": int(row[2]),
        "avg_order_value": float(row[3]),
        "date_from": str(date_from),
        "date_to": str(date_to),
    }


def fetch_revenue_trends(date_from: date, date_to: date, granularity: str) -> list[dict]:
    """
    Returns revenue trend buckets between date_from and date_to.
    granularity: daily | weekly | monthly
    """
    granularity_map = {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
    }
    if granularity not in granularity_map:
        raise ValueError("granularity must be one of: daily, weekly, monthly")

    trunc_unit = granularity_map[granularity]

    sql = """
        SELECT
            DATE_TRUNC(%s, created_at)::date AS bucket,
            COALESCE(SUM(order_amount), 0) AS revenue,
            COUNT(*) AS orders,
            COUNT(DISTINCT customer_key) AS unique_customers
        FROM fact_orders
        WHERE created_at::date BETWEEN %s AND %s
        GROUP BY 1
        ORDER BY 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [trunc_unit, date_from, date_to])
        rows = cursor.fetchall()

    return [
        {
            "bucket": str(r[0]),
            "revenue": float(r[1]),
            "orders": int(r[2]),
            "unique_customers": int(r[3]),
        }
        for r in rows
    ]
