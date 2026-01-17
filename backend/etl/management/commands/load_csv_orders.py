import os
from datetime import datetime
from decimal import Decimal

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from analytics.models import DimCustomer, DimProduct, DimTime, FactOrder
from etl.models import ETLRun


def to_decimal(x) -> Decimal:
    try:
        return Decimal(str(x)).quantize(Decimal("0.01"))
    except Exception:
        return Decimal("0.00")


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

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options["path"]
        source = options["source"]
        job_name = options["job"]

        run = ETLRun.objects.create(source=source, job_name=job_name, status=ETLRun.Status.RUNNING)

        try:
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV not found at: {csv_path}")

            df = pd.read_csv(csv_path)
            run.rows_extracted = len(df)

            required_cols = {
                "order_id", "customer_id", "email", "country", "city",
                "product_id", "product_name", "category", "price",
                "quantity", "discount_amount", "created_at"
            }
            missing = required_cols - set(df.columns)
            if missing:
                raise ValueError(f"Missing columns: {sorted(list(missing))}")

            # Clean + type conversions
            df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
            df = df.dropna(subset=["order_id", "customer_id", "product_id", "created_at"])
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
            df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
            df["discount_amount"] = pd.to_numeric(df["discount_amount"], errors="coerce").fillna(0.0)

            loaded = 0

            for row in df.to_dict(orient="records"):
                created_at: datetime = row["created_at"].to_pydatetime()
                if timezone.is_naive(created_at):
                    created_at = timezone.make_aware(created_at)

                # DimTime (date grain)
                d = created_at.date()
                time_dim, _ = DimTime.objects.get_or_create(
                    date=d,
                    defaults={
                        "year": d.year,
                        "month": d.month,
                        "day": d.day,
                        "week": int(d.strftime("%W")),
                    },
                )

                # DimCustomer upsert (simple Type 1 now)
                customer, _ = DimCustomer.objects.get_or_create(
                    customer_id=row["customer_id"],
                    defaults={
                        "email": row.get("email"),
                        "country": row.get("country"),
                        "city": row.get("city"),
                        "created_at": created_at,
                    },
                )
                # Optional: update missing fields if already exists
                updated = False
                for field in ["email", "country", "city"]:
                    val = row.get(field)
                    if val and getattr(customer, field) != val:
                        setattr(customer, field, val)
                        updated = True
                if updated:
                    customer.save(update_fields=["email", "country", "city"])

                # DimProduct upsert
                product, _ = DimProduct.objects.get_or_create(
                    product_id=row["product_id"],
                    defaults={
                        "name": row.get("product_name"),
                        "category": row.get("category"),
                        "price": to_decimal(row.get("price")),
                    },
                )
                # Update name/category/price if changed
                prod_updated = False
                if row.get("product_name") and product.name != row.get("product_name"):
                    product.name = row.get("product_name")
                    prod_updated = True
                if row.get("category") and product.category != row.get("category"):
                    product.category = row.get("category")
                    prod_updated = True
                price_dec = to_decimal(row.get("price"))
                if price_dec and product.price != price_dec:
                    product.price = price_dec
                    prod_updated = True
                if prod_updated:
                    product.save(update_fields=["name", "category", "price"])

                # FactOrder idempotent load (order_id unique)
                if FactOrder.objects.filter(order_id=row["order_id"]).exists():
                    continue

                qty = int(row.get("quantity", 1))
                price = to_decimal(row.get("price"))
                discount_amount = to_decimal(row.get("discount_amount"))
                gross = (price * qty).quantize(Decimal("0.01"))
                net = (gross - discount_amount).quantize(Decimal("0.01"))
                if net < 0:
                    net = Decimal("0.00")

                FactOrder.objects.create(
                    order_id=row["order_id"],
                    customer=customer,
                    product=product,
                    time=time_dim,
                    order_amount=net,
                    quantity=qty,
                    discount_amount=discount_amount,
                    created_at=created_at,
                )
                loaded += 1

            run.status = ETLRun.Status.SUCCESS
            run.rows_loaded = loaded
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "rows_extracted", "rows_loaded", "finished_at"])

            self.stdout.write(self.style.SUCCESS(f"✅ ETL Success. Extracted={run.rows_extracted}, Loaded={loaded}"))

        except Exception as e:
            run.status = ETLRun.Status.FAILED
            run.error_message = str(e)
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "error_message", "finished_at", "rows_extracted"])

            raise
