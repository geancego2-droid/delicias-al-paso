from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import Product, Sale, Purchase, Expense, Customer, Supplier, Category
from .forms import SaleForm, SaleItemFormSet, PurchaseForm, PurchaseItemFormSet, ProductForm, ExpenseForm, CustomerForm, SupplierForm, CategoryForm
from .services import register_sale, register_purchase

@login_required
def dashboard(request):
    today = date.today(); products = Product.objects.filter(active=True)
    low_stock = products.filter(stock__lte=F('minimum_stock')).order_by('stock')[:10]
    sales_today = Sale.objects.filter(sold_at=today).aggregate(total=Sum('total'))['total'] or 0
    sales_month = Sale.objects.filter(sold_at__year=today.year, sold_at__month=today.month).aggregate(total=Sum('total'))['total'] or 0
    expenses_month = Expense.objects.filter(date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0
    receivable = sum((s.balance_due for s in Sale.objects.filter(customer__isnull=False)), 0)
    stock_value = sum((p.stock * p.cost_price for p in products), 0)
    return render(request, 'stock/dashboard.html', locals())

@login_required
@require_http_methods(['GET','POST'])
def new_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False); sale.created_by = request.user; sale.save()
            items = SaleItemFormSet(request.POST, instance=sale)
            if items.is_valid():
                pending = items.save(commit=False)
                for item in pending:
                    if item.product_id:
                        item.unit_cost = item.product.cost_price
                        if not item.unit_price: item.unit_price = item.product.sale_price
                        item.save()
                for item in items.deleted_objects: item.delete()
                try:
                    register_sale(sale, request.user); messages.success(request, f'Venta #{sale.pk} registrada correctamente.'); return redirect('stock-dashboard')
                except Exception as e: sale.delete(); messages.error(request, str(e))
            else: sale.delete(); form.add_error(None, 'Revisa los productos de la venta.')
    else: form = SaleForm(); items = SaleItemFormSet()
    return render(request, 'stock/new_sale.html', {'form': form, 'items': items, 'title': 'Nueva venta'})

@login_required
@require_http_methods(['GET','POST'])
def new_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False); purchase.created_by = request.user; purchase.save(); items = PurchaseItemFormSet(request.POST, instance=purchase)
            if items.is_valid():
                items.save()
                try: register_purchase(purchase, request.user); messages.success(request, f'Compra #{purchase.pk} registrada correctamente.'); return redirect('stock-dashboard')
                except Exception as e: purchase.delete(); messages.error(request, str(e))
            else: purchase.delete(); form.add_error(None, 'Revisa los productos de la compra.')
    else: form = PurchaseForm(); items = PurchaseItemFormSet()
    return render(request, 'stock/new_purchase.html', {'form': form, 'items': items, 'title': 'Nueva compra'})

@login_required
def products(request):
    qs = Product.objects.filter(active=True).select_related('category','supplier'); q = request.GET.get('q','').strip()
    if q: qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
    return render(request, 'stock/products.html', {'products': qs, 'q': q})

@login_required
@require_http_methods(['GET','POST'])
def new_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request, 'Producto creado correctamente.'); return redirect('products')
    return render(request, 'stock/product_form.html', {'form': form, 'title': 'Nuevo producto'})

@login_required
@require_http_methods(['GET','POST'])
def edit_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save(); messages.success(request, 'Producto actualizado correctamente.'); return redirect('products')
    return render(request, 'stock/product_form.html', {'form': form, 'title': 'Editar producto', 'product': product})

@login_required
def customers(request):
    customers = Customer.objects.all(); data=[]
    for customer in customers:
        sales = Sale.objects.filter(customer=customer); debt=sum((s.balance_due for s in sales), 0); data.append((customer,debt))
    return render(request, 'stock/customers.html', {'data': data})

@login_required
@require_http_methods(['GET','POST'])
def new_customer(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Cliente creado correctamente.'); return redirect('customers')
    return render(request, 'stock/contact_form.html', {'form': form, 'title': 'Nuevo cliente', 'icon': '👥'})

@login_required
@require_http_methods(['GET','POST'])
def edit_customer(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save(); messages.success(request, 'Cliente actualizado correctamente.'); return redirect('customers')
    return render(request, 'stock/contact_form.html', {'form': form, 'title': 'Editar cliente', 'icon': 'Editar', 'customer': customer})

@login_required
def suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'stock/suppliers.html', {'suppliers': suppliers})

@login_required
@require_http_methods(['GET','POST'])
def new_supplier(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Proveedor creado correctamente.'); return redirect('suppliers')
    return render(request, 'stock/contact_form.html', {'form': form, 'title': 'Nuevo proveedor', 'icon': '🏢'})

@login_required
@require_http_methods(['GET','POST'])
def edit_supplier(request, supplier_id):
    supplier = Supplier.objects.get(pk=supplier_id)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save(); messages.success(request, 'Proveedor actualizado correctamente.'); return redirect('suppliers')
    return render(request, 'stock/contact_form.html', {'form': form, 'title': 'Editar proveedor', 'icon': 'Editar', 'supplier': supplier})

@login_required
@require_http_methods(['GET','POST'])
def categories(request):
    categories = Category.objects.all()
    return render(request, 'stock/categories.html', {'categories': categories})

@login_required
@require_http_methods(['GET','POST'])
def new_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Categoría creada correctamente.'); return redirect('categories')
    return render(request, 'stock/contact_form.html', {'form': form, 'title': 'Nueva categoría', 'icon': '🏷️'})


@login_required
@require_http_methods(['GET', 'POST'])
def new_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.created_by = request.user
        expense.save()
        messages.success(request, f'Gasto de Gs. {expense.amount:,.0f} registrado correctamente.')
        return redirect('stock-dashboard')
    return render(request, 'stock/expense_form.html', {'form': form, 'title': 'Registrar gasto'})
