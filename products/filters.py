import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    FilterSet for Product API supporting category, price ranges, and name filtering.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Product Name contains'
    )
    category = django_filters.CharFilter(
        method='filter_by_category',
        label='Category ID or Category Name'
    )
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        label='Category Name contains'
    )

    def filter_by_category(self, queryset, name, value):
        if not value:
            return queryset
        if value.isdigit():
            return queryset.filter(category__id=int(value))
        return queryset.filter(category__name__icontains=value)
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Minimum Price'
    )
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Maximum Price'
    )
    price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='exact',
        label='Exact Price'
    )

    class Meta:
        model = Product
        fields = ['category', 'category_name', 'name', 'price', 'min_price', 'max_price']
