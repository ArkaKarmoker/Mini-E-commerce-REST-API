from decimal import Decimal
from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    products_count = serializers.IntegerField(
        source='products.count',
        read_only=True
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'products_count']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Product Review and Rating.
    """
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False
    )

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'user_id', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        product = attrs.get('product') or self.context.get('product')
        user = getattr(request, 'user', None) if request else None

        # If creating a review, validate order status and uniqueness
        if self.instance is None and user and user.is_authenticated and product:
            # 1. Ensure user has purchased the product and order status is 'Completed'
            from orders.models import Order
            has_completed_order = Order.objects.filter(
                user=user,
                product=product,
                status='Completed'
            ).exists()
            if not has_completed_order:
                raise serializers.ValidationError(
                    {"detail": "You can only review products that you have purchased and received (order status must be 'Completed')."}
                )

            # 2. Ensure user hasn't already reviewed this product
            if Review.objects.filter(product=product, user=user).exists():
                raise serializers.ValidationError(
                    {"detail": "You have already submitted a review for this product."}
                )
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product list and create/update operations.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'category',
            'category_name',
            'image',
            'average_rating',
            'total_reviews',
            'created_date',
            'updated_date',
        ]
        read_only_fields = [
            'id',
            'category_name',
            'average_rating',
            'total_reviews',
            'created_date',
            'updated_date',
        ]

    def validate_price(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Price must be greater than 0.00.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class ProductDetailSerializer(ProductSerializer):
    """
    Detailed Product Serializer including full category details and recent reviews.
    """
    category = CategorySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews']
