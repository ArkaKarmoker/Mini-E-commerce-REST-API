"""
URL configuration for core project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from orders.views import OrderViewSet
from products.views import CategoryViewSet, ProductViewSet, ReviewViewSet


class APIRootView(APIView):
    """
    API Root endpoint providing navigation links to all available resources.
    """
    @extend_schema(
        summary="API Root Index",
        description="Provides interactive links to all documentation interfaces and primary endpoints.",
        responses={200: OpenApiResponse(description="API resources and documentation endpoints")}
    )
    def get(self, request, format=None):
        return Response({
            "message": "Welcome to Mini E-commerce REST API",
            "documentation": {
                "swagger_ui": request.build_absolute_uri('/api/docs/'),
                "redoc": request.build_absolute_uri('/api/redoc/'),
                "openapi_schema": request.build_absolute_uri('/api/schema/'),
            },
            "endpoints": {
                "auth_register": request.build_absolute_uri('/api/auth/register/'),
                "auth_login": request.build_absolute_uri('/api/auth/login/'),
                "auth_logout": request.build_absolute_uri('/api/auth/logout/'),
                "auth_profile": request.build_absolute_uri('/api/auth/profile/'),
                "categories": request.build_absolute_uri('/api/categories/'),
                "products": request.build_absolute_uri('/api/products/'),
                "orders": request.build_absolute_uri('/api/orders/'),
                "reviews": request.build_absolute_uri('/api/reviews/'),
            }
        })


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Root
    path('', APIRootView.as_view(), name='api-root-index'),
    path('api/', APIRootView.as_view(), name='api-root'),

    # Interactive API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication & User Management
    path('api/auth/', include('accounts.urls', namespace='accounts')),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),

    # Routers mounted at /api/ (e.g. /api/products/, /api/categories/, /api/orders/)
    path('api/', include(router.urls)),

    # Also mounted at root (e.g. /products/, /categories/, /orders/) for direct access
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
