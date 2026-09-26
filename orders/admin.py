from django.contrib import admin
from django.utils.html import format_html
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'status_badge', 'order_date')
    list_display_links = ('id', 'product')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'product__name', 'id')
    ordering = ('-order_date',)

    def status_badge(self, obj):
        colors = {
            'Pending': '#d97706',     # Warm Amber
            'Processing': '#2563eb',  # Royal Blue
            'Completed': '#059669',   # Forest Green
            'Cancelled': '#dc2626',   # Crimson Red
        }
        bg_color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: #ffffff; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px; letter-spacing: 0.5px;">{}</span>',
            bg_color,
            obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
