from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Category, Supplier, Customer, CustomerPayment, Product, Purchase, PurchaseItem, Sale, SaleItem, Expense, StockMovement
from .services import register_purchase, register_sale, apply_stock

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "ruc", "phone")
    search_fields = ("name", "ruc", "phone")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "document", "phone", "credit_limit")
    search_fields = ("name", "document", "phone")

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_date','customer','amount','payment_method','created_by')
    list_filter = ('payment_date','payment_method')
    search_fields = ('customer__name','customer__document')
    readonly_fields = ('created_by',)
    def save_form(self, request, form, change):
        obj=super().save_form(request,form,change)
        if not obj.created_by_id: obj.created_by=request.user
        return obj

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "cost_price", "sale_price", "stock", "minimum_stock", "active")
    list_filter = ("active", "category")
    search_fields = ("code", "name")
    readonly_fields = ("stock",)

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ("product", "quantity", "unit_cost", "subtotal_display")
    readonly_fields = ("subtotal_display",)
    def subtotal_display(self, obj): return obj.subtotal if obj.pk else 0
    subtotal_display.short_description = "Subtotal (Gs.)"

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "purchased_at", "supplier", "invoice_number", "total", "created_by")
    list_filter = ("purchased_at", "supplier")
    search_fields = ("invoice_number", "supplier__name")
    readonly_fields = ("total", "created_by")
    inlines = (PurchaseItemInline,)
    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        if not obj.created_by_id: obj.created_by = request.user
        return obj
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change:
            try: register_purchase(form.instance, request.user)
            except ValidationError as e: messages.error(request, str(e))

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ("product", "quantity", "unit_price", "unit_cost", "subtotal_display")
    readonly_fields = ("unit_cost", "subtotal_display")
    def subtotal_display(self, obj): return obj.subtotal if obj.pk else 0
    subtotal_display.short_description = "Subtotal (Gs.)"

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "sold_at", "customer", "payment_method", "total", "paid", "balance_due", "created_by")
    list_filter = ("sold_at", "payment_method")
    search_fields = ("customer__name",)
    readonly_fields = ("total", "created_by")
    inlines = (SaleItemInline,)
    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        if not obj.created_by_id: obj.created_by = request.user
        return obj
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change:
            try: register_sale(form.instance, request.user)
            except ValidationError as e: messages.error(request, str(e))

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "description", "amount", "paid_from_cash", "created_by")
    list_filter = ("date", "category", "paid_from_cash")
    search_fields = ("description",)
    readonly_fields = ("created_by",)
    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        if not obj.created_by_id: obj.created_by = request.user
        return obj

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "product", "movement_type", "quantity", "reason", "user")
    list_filter = ("movement_type", "created_at")
    search_fields = ("product__name", "product__code", "reason")
    readonly_fields = ("created_at", "updated_at", "product", "movement_type", "quantity", "reason", "user")

admin.site.site_header = "DELICIAS AL PASO — Control de Stock"
admin.site.site_title = "Control de Stock"
admin.site.index_title = "Administración del negocio"
