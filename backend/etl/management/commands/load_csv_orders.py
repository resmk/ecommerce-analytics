import os
from django.core.management.base import BaseCommand
from etl.jobs.load_csv_orders_job import run_load_csv_orders


class Command(BaseCommand):
    help = "Load orders CSV into warehouse tables (dims + fact) with audit logging."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default=os.path.join("..", "data", "raw", "orders.csv"),
            help="Path to orders CSV file",
        )
        parser.add_argument("--source", type=str, default="csv")
        parser.add_argument("--job", type=str, default="load_csv_orders")

    def handle(self, *args, **options):
        run = run_load_csv_orders(
            csv_path=options["path"],
            source=options["source"],
            job_name=options["job"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ ETL {run.status}. Extracted={run.rows_extracted}, Loaded={run.rows_loaded}"
            )
        )
