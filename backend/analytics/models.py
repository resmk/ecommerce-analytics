from django.db import models


class DimCustomer(models.Model):
    customer_key = models.BigAutoField(primary_key=True)
    customer_id = models.CharField(max_length=64, unique=True)  # source/business id
    email = models.EmailField(blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)  # source timestamp if available

    # SCD-ready fields (Type 2 later)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        db_table = "dim_customers"
        indexes = [
            models.Index(fields=["customer_id"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.customer_id}"


class DimProduct(models.Model):
    product_key = models.BigAutoField(primary_key=True)
    product_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=128, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = "dim_products"
        indexes = [
            models.Index(fields=["product_id"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.product_id}"


class DimTime(models.Model):
    time_key = models.BigAutoField(primary_key=True)
    date = models.DateField(unique=True)
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    week = models.IntegerField()

    class Meta:
        db_table = "dim_time"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["year", "month"]),
        ]

    def __str__(self):
        return str(self.date)


class FactOrder(models.Model):
    order_key = models.BigAutoField(primary_key=True)
    order_id = models.CharField(max_length=64, unique=True)  # source/business id

    customer = models.ForeignKey(DimCustomer, on_delete=models.PROTECT, db_column="customer_key")
    product = models.ForeignKey(DimProduct, on_delete=models.PROTECT, db_column="product_key")
    time = models.ForeignKey(DimTime, on_delete=models.PROTECT, db_column="time_key")

    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField()  # event time
    ingested_at = models.DateTimeField(auto_now_add=True)  # load time

    class Meta:
        db_table = "fact_orders"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["time"]),
        ]

    def __str__(self):
        return f"{self.order_id}"
