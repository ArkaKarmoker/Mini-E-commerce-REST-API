from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from accounts.serializers import UserSerializer
from products.models import Product
from products.serializers import ProductSerializer
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing Orders.
    Includes user details, product summary, stock validation, and total price calculation.
    """
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True
    )
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    order_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'total_price',
            'status',
            'order_date',
        ]
        read_only_fields = [
            'id',
            'user',
            'user_id',
            'product_name',
            'product_price',
            'total_price',
            'order_date',
            'status',
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)

        # Stock validation
        if product.stock < quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"Insufficient stock for '{product.name}'. "
                        f"Available stock: {product.stock}, requested: {quantity}."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        product = validated_data['product']
        quantity = validated_data['quantity']

        # Use transaction and select_for_update to handle concurrency safely
        with transaction.atomic():
            locked_product = Product.objects.select_for_update().get(pk=product.pk)
            if locked_product.stock < quantity:
                raise serializers.ValidationError(
                    {
                        "quantity": (
                            f"Insufficient stock for '{locked_product.name}'. "
                            f"Available stock: {locked_product.stock}, requested: {quantity}."
                        )
                    }
                )

            # Deduct stock
            locked_product.stock -= quantity
            locked_product.save(update_fields=['stock'])

            # Compute total price
            total_price = locked_product.price * quantity

            order = Order.objects.create(
                user=user,
                product=locked_product,
                quantity=quantity,
                total_price=total_price,
            )

        return order
