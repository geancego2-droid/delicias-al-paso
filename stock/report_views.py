from datetime import date
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.shortcuts import render
from .models import Product, Sale, SaleItem, Purchase, Expense, CustomerPayment

@login_required
def reports(request):
    today=date.today(); year=int(request.GET.get('year',today.year)); month=int(request.GET.get('month',today.month))
    sales=Sale.objects.filter(sold_at__year=year,sold_at__month=month)
    purchases=Purchase.objects.filter(purchased_at__year=year,purchased_at__month=month)
    expenses=Expense.objects.filter(date__year=year,date__month=month)
    payments=CustomerPayment.objects.filter(payment_date__year=year,payment_date__month=month)
    sales_total=sales.aggregate(v=Sum('total'))['v'] or Decimal(0)
    purchases_total=purchases.aggregate(v=Sum('total'))['v'] or Decimal(0)
    expenses_total=expenses.aggregate(v=Sum('amount'))['v'] or Decimal(0)
    collections=payments.aggregate(v=Sum('amount'))['v'] or Decimal(0)
    cost=SaleItem.objects.filter(sale__in=sales).aggregate(v=Sum(ExpressionWrapper(F('quantity')*F('unit_cost'),output_field=DecimalField(max_digits=18,decimal_places=0))))['v'] or Decimal(0)
    gross_profit=sales_total-cost; net_profit=gross_profit-expenses_total
    receivable=sum((s.balance_due for s in Sale.objects.filter(customer__isnull=False)),Decimal(0))
    stock_value=sum((p.stock*p.cost_price for p in Product.objects.filter(active=True)),Decimal(0))
    return render(request,'stock/reports.html',locals())
