import os
from celery import shared_task
from etl.jobs.load_csv_orders_job import run_load_csv_orders


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def load_csv_orders_task(self):
    """
    Scheduled ETL task: loads CSV orders into warehouse.
    Retries automatically on failure.
    """
    csv_path = os.getenv("ETL_CSV_ORDERS_PATH", "../data/raw/orders.csv")
    run = run_load_csv_orders(csv_path=csv_path, source="csv", job_name="celery_load_csv_orders")
    return {
        "run_id": run.run_id,
        "status": run.status,
        "rows_extracted": run.rows_extracted,
        "rows_loaded": run.rows_loaded,
    }
