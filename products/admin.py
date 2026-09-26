from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_thumbnail', 'name', 'category', 'price', 'stock', 'average_rating', 'created_date')
    list_display_links = ('id', 'image_thumbnail', 'name')
    list_filter = ('category', 'created_date')
    search_fields = ('name', 'description')
    ordering = ('-created_date',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />', obj.image.url)
        return "-"
    image_thumbnail.short_description = "Image"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
