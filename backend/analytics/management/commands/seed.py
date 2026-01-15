import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from analytics.models import DimCustomer, DimProduct, DimTime, FactOrder


class Command(BaseCommand):
    help = "Seed the database with sample dimension and fact data."

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=200)
        parser.add_argument("--products", type=int, default=50)
        parser.add_argument("--orders", type=int, default=500)
        parser.add_argument("--days", type=int, default=180)

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()

        n_customers = options["customers"]
        n_products = options["products"]
        n_orders = options["orders"]
        n_days = options["days"]

        self.stdout.write(self.style.WARNING("Seeding started..."))

        # 1) DimTime: create last N days (idempotent via get_or_create)
        start = date.today() - timedelta(days=n_days)
        for i in range(n_days + 1):
            d = start + timedelta(days=i)
            DimTime.objects.get_or_create(
                date=d,
                defaults={
                    "year": d.year,
                    "month": d.month,
                    "day": d.day,
                    "week": int(d.strftime("%W")),
                },
            )

        # 2) Customers (idempotent by customer_id unique)
        customers = []
        for i in range(n_customers):
            cust_id = f"CUST-{i+1:06d}"
            obj, _ = DimCustomer.objects.get_or_create(
                customer_id=cust_id,
                defaults={
                    "email": fake.email(),
                    "country": fake.country(),
                    "city": fake.city(),
                    "created_at": fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.get_current_timezone()),
                },
            )
            customers.append(obj)

        # 3) Products (idempotent by product_id unique)
        categories = ["Electronics", "Home", "Fashion", "Beauty", "Sports", "Books", "Toys"]
        products = []
        for i in range(n_products):
            prod_id = f"PROD-{i+1:06d}"
            obj, _ = DimProduct.objects.get_or_create(
                product_id=prod_id,
                defaults={
                    "name": fake.catch_phrase(),
                    "category": random.choice(categories),
                    "price": Decimal(str(round(random.uniform(5, 300), 2))),
                },
            )
            products.append(obj)

        # 4) Orders (idempotent by order_id unique)
        # Create orders across the last N days.
        all_dates = list(DimTime.objects.order_by("date").values_list("date", flat=True))
        created_count = 0

        for i in range(n_orders):
            order_id = f"ORD-{i+1:08d}"
            if FactOrder.objects.filter(order_id=order_id).exists():
                continue

            cust = random.choice(customers)
            prod = random.choice(products)

            d = random.choice(all_dates)
            # Random time in day:
            created_at = timezone.make_aware(
                fake.date_time_between_dates(
                    datetime_start=timezone.datetime(d.year, d.month, d.day, 0, 0, 0),
                    datetime_end=timezone.datetime(d.year, d.month, d.day, 23, 59, 59),
                )
            )

            time_dim = DimTime.objects.get(date=d)

            qty = random.randint(1, 5)
            base_price = prod.price or Decimal("10.00")
            discount = Decimal(str(round(random.uniform(0, 0.25), 2)))  # up to 25%
            gross = base_price * qty
            discount_amount = (gross * discount).quantize(Decimal("0.01"))
            net = (gross - discount_amount).quantize(Decimal("0.01"))

            FactOrder.objects.create(
                order_id=order_id,
                customer=cust,
                product=prod,
                time=time_dim,
                order_amount=net,
                quantity=qty,
                discount_amount=discount_amount,
                created_at=created_at,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seed complete. Created {created_count} new orders."))
