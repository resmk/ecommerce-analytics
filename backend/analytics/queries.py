from datetime import date
from django.db import connection


def fetch_kpis(date_from: date, date_to: date) -> dict:
    """
    Returns basic KPI metrics for orders between date_from and date_to (inclusive).
    Uses raw SQL for performance + clarity (and to show SQL skills).
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
