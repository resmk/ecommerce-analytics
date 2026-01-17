from rest_framework import serializers
from analytics.models import FactOrder


class FactOrderSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(source="customer.customer_id", read_only=True)
    product_id = serializers.CharField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_category = serializers.CharField(source="product.category", read_only=True)

    class Meta:
        model = FactOrder
        fields = [
            "order_id",
            "created_at",
            "order_amount",
            "quantity",
            "discount_amount",
            "customer_id",
            "product_id",
            "product_name",
            "product_category",
        ]
