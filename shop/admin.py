from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Contact, Order, OrderUpdate

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 📝 Columns displayed in the main admin table view grid
    list_display = ('product_name', 'category', 'price', 'stock')
    
    # 🔍 Instant search bar query mappings
    search_fields = ('product_name', 'category', 'description')
    
    # 🧭 Right-hand sidebar filtering criteria matrix
    list_filter = ('category', 'price')
    
    # ✏️ Allows changing prices and stock directly from the list view without clicking into the item page
    list_editable = ('price', 'stock')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'email', 'amount', 'payment_status', 'razorpay_order_id')
    list_filter = ('payment_status',)
    search_fields = ('name', 'email', 'order_id', 'razorpay_order_id')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'related_updates_log')

    def related_updates_log(self, obj):
        updates = OrderUpdate.objects.filter(order_id=obj.order_id).order_by('-timestamp')
        if not updates.exists():
            return "No tracking updates recorded."
        html = "<table style='width:100%; border-collapse:collapse; border:1px solid #ddd;'><thead><tr style='background:#f5f5f5;'><th style='padding:6px; border:1px solid #ddd; text-align:left;'>Date</th><th style='padding:6px; border:1px solid #ddd; text-align:left;'>Status Update</th></tr></thead><tbody>"
        for u in updates:
            html += f"<tr><td style='padding:6px; border:1px solid #ddd;'>{u.timestamp}</td><td style='padding:6px; border:1px solid #ddd;'>{u.update_desc}</td></tr>"
        html += "</tbody></table>"
        return format_html(html)

    related_updates_log.short_description = "Related Tracking Updates (Matched by Order ID)"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'desc')


@admin.register(OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'order_id', 'update_desc', 'timestamp')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)