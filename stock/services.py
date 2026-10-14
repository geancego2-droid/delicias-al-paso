from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, StockMovement

@transaction.atomic
def apply_stock(product, quantity, movement_type, reason, user=None):
    product = Product.objects.select_for_update().get(pk=product.pk)
    if movement_type == "IN":
        delta = quantity
    elif movement_type == "OUT":
        delta = -quantity
    elif movement_type == "ADJUST":
        delta = quantity - product.stock
    else:
        raise ValidationError("Tipo de movimiento inválido.")
    new_stock = product.stock + delta
    if new_stock < 0:
        raise ValidationError(f"Stock insuficiente para {product.name}. Disponible: {product.stock}.")
    product.stock = new_stock
    product.save(update_fields=["stock", "updated_at"])
    if delta:
        StockMovement.objects.create(product=product, movement_type=movement_type, quantity=delta, reason=reason, user=user)
    return product

@transaction.atomic
def register_purchase(purchase, user=None):
    total = 0
    for item in purchase.items.select_related("product"):
        total += item.subtotal
        apply_stock(item.product, item.quantity, "IN", f"Compra #{purchase.pk}", user)
    purchase.total = total
    purchase.save(update_fields=["total", "updated_at"])
    return purchase

@transaction.atomic
def register_sale(sale, user=None):
    total = 0
    for item in sale.items.select_related("product"):
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if product.stock < item.quantity:
            raise ValidationError(f"Stock insuficiente para {product.name}. Disponible: {product.stock}.")
        item.unit_cost = product.cost_price
        item.save(update_fields=["unit_cost", "updated_at"])
        total += item.subtotal
        apply_stock(product, item.quantity, "OUT", f"Venta #{sale.pk}", user)
    sale.total = total
    sale.paid = min(sale.paid, total)
    sale.save(update_fields=["total", "paid", "updated_at"])
    return sale
