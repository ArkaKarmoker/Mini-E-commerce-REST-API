from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Category, Product, Review
from .pagination import StandardResultsSetPagination
from .permissions import IsAdminOrReadOnly, IsReviewAuthorOrReadOnly
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductSerializer,
    ReviewSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List all categories", description="Retrieve a list of all product categories."),
    retrieve=extend_schema(summary="Get single category", description="Retrieve details of a specific category by ID."),
    create=extend_schema(summary="Create a category", description="Create a new category (Admin/Staff only)."),
    update=extend_schema(summary="Update a category", description="Update an existing category (Admin/Staff only)."),
    partial_update=extend_schema(summary="Partial update a category", description="Partially update a category (Admin/Staff only)."),
    destroy=extend_schema(summary="Delete a category", description="Delete a category (Admin/Staff only)."),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations:
    - View all categories (Public)
    - View single category (Public)
    - Create category (Staff/Admin)
    - Update category (Staff/Admin)
    - Delete category (Staff/Admin)
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


@extend_schema_view(
    list=extend_schema(
        summary="List all products with filtering, searching, and ordering",
        description="""
        Retrieve paginated list of products.
        Supports:
        - Search by product name or description: `?search=phone`
        - Filter by category ID: `?category=1`
        - Filter by category name: `?category_name=Electronics`
        - Filter by price: `?min_price=100&max_price=500` or `?price=100`
        - Order by price or other fields: `?ordering=price` (ascending) or `?ordering=-price` (descending)
        - Pagination: `?page=1&page_size=10`
        """,
        parameters=[
            OpenApiParameter('search', str, description='Search products by name or description'),
            OpenApiParameter('category', int, description='Filter by Category ID'),
            OpenApiParameter('category_name', str, description='Filter by Category Name'),
            OpenApiParameter('min_price', float, description='Filter products with price greater than or equal to this'),
            OpenApiParameter('max_price', float, description='Filter products with price less than or equal to this'),
            OpenApiParameter('price', float, description='Filter products with exact price'),
            OpenApiParameter('ordering', str, description='Order by field (e.g. price, -price, created_date, -created_date)'),
            OpenApiParameter('page', int, description='Page number'),
            OpenApiParameter('page_size', int, description='Page size'),
        ]
    ),
    retrieve=extend_schema(summary="Get product details", description="Retrieve detailed information about a single product."),
    create=extend_schema(summary="Add a product", description="Add a new product (Staff/Admin only)."),
    update=extend_schema(summary="Update a product", description="Update a product (Staff/Admin only)."),
    partial_update=extend_schema(summary="Partial update a product", description="Partially update a product (Staff/Admin only)."),
    destroy=extend_schema(summary="Delete a product", description="Delete a product (Staff/Admin only)."),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations, filtering, searching, ordering, and pagination.
    """
    queryset = Product.objects.select_related('category').prefetch_related('reviews__user').all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_date', 'name', 'stock']
    ordering = ['-created_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    @extend_schema(
        summary="List or create reviews for this product",
        description="GET: list all reviews. POST: create a review (requires authentication).",
        request=ReviewSerializer,
        responses={200: ReviewSerializer(many=True), 201: ReviewSerializer}
    )
    @action(
        detail=True,
        methods=['get', 'post'],
        permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    )
    def reviews(self, request, pk=None):
        """
        Custom action to view or submit reviews for a specific product.
        """
        product = self.get_object()

        if request.method == 'GET':
            reviews = product.reviews.select_related('user').all()
            serializer = ReviewSerializer(reviews, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            # Check if user has an order with status 'Completed'
            from orders.models import Order
            has_completed_order = Order.objects.filter(
                user=request.user,
                product=product,
                status='Completed'
            ).exists()
            if not has_completed_order:
                return Response(
                    {"detail": "You can only review products that you have purchased and received (order status must be 'Completed')."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user already reviewed
            if Review.objects.filter(product=product, user=request.user).exists():
                return Response(
                    {"detail": "You have already submitted a review for this product."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ReviewSerializer(
                data=request.data,
                context={'request': request, 'product': product}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual reviews.
    """
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
