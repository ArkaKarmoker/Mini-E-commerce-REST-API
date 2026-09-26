from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from products.pagination import StandardResultsSetPagination
from .models import Order
from .serializers import OrderSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List user orders",
        description="Retrieve a paginated list of orders placed by the authenticated user."
    ),
    retrieve=extend_schema(
        summary="Get single order details",
        description="Retrieve details of a single order belonging to the authenticated user."
    ),
    create=extend_schema(
        summary="Create a new order",
        description="Place a new order for a product. Automatically checks and deducts stock, and computes total price."
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Orders:
    - Authenticated users can create orders.
    - Authenticated users can view only their own orders.
    - Authenticated users can view details of a single order they own.
    - Users can cancel their pending order (which restores product stock).
    - Staff/Admin can view all orders across all users.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'post', 'head', 'options']

    queryset = Order.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request:
            return Order.objects.none()
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        if user.is_staff:
            return Order.objects.select_related('user', 'product').all().order_by('-order_date')
        return Order.objects.select_related('user', 'product').filter(user=user).order_by('-order_date')

    @extend_schema(
        summary="Cancel an order",
        description="Cancel a pending order. Automatically restores product stock.",
        responses={
            200: OpenApiResponse(description="Order cancelled successfully"),
            400: OpenApiResponse(description="Cannot cancel an order that is not pending"),
        }
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a pending order and refund the product stock.
        """
        order = self.get_object()

        if order.status != 'Pending':
            return Response(
                {"error": f"Order cannot be cancelled because its status is '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            product = order.product
            product.stock += order.quantity
            product.save(update_fields=['stock'])

            order.status = 'Cancelled'
            order.save(update_fields=['status'])

        return Response(
            {
                "message": f"Order #{order.id} cancelled successfully and {order.quantity} item(s) restored to stock.",
                "order": OrderSerializer(order, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )
