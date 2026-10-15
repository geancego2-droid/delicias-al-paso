from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import CashSession, CashMovement, Sale, Purchase, Expense, CustomerPayment

@login_required
def cash_register(request):
    session = CashSession.objects.filter(status="OPEN").first()
    if request.method == "POST" and not session:
        amount = Decimal(request.POST.get("opening_amount", "0") or 0)
        session = CashSession.objects.create(opening_amount=amount, opened_by=request.user)
        messages.success(request, "Caja abierta correctamente."); return redirect("cash_register")
    today = timezone.localdate()
    sales = Sale.objects.filter(sold_at=today, payment_method="CASH", created_by__isnull=False).aggregate(total=Sum("total"))["total"] or 0
    purchases = Purchase.objects.filter(purchased_at=today, paid_from_cash=True).aggregate(total=Sum("total"))["total"] or 0
    expenses = Expense.objects.filter(date=today, paid_from_cash=True).aggregate(total=Sum("amount"))["total"] or 0
    customer_payments = CustomerPayment.objects.filter(payment_date=today, payment_method="CASH").aggregate(total=Sum("amount"))["total"] or 0
    ins = session.movements.filter(movement_type="IN").aggregate(t=Sum("amount"))["t"] or 0 if session else 0
    outs = session.movements.filter(movement_type="OUT").aggregate(t=Sum("amount"))["t"] or 0 if session else 0
    expected = (session.opening_amount if session else 0) + sales + customer_payments + ins - purchases - expenses - outs
    return render(request, "stock/cash.html", {"session":session,"sales":sales,"purchases":purchases,"expenses":expenses,"customer_payments":customer_payments,"ins":ins,"outs":outs,"expected":expected})

@login_required
def cash_movement(request):
    session = CashSession.objects.filter(status="OPEN").first()
    if not session: messages.error(request,"Primero debe abrir la caja."); return redirect("cash_register")
    if request.method == "POST":
        CashMovement.objects.create(session=session,movement_type=request.POST["movement_type"],amount=Decimal(request.POST["amount"]),description=request.POST["description"],user=request.user)
        return redirect("cash_register")
    return render(request,"stock/cash_movement.html")

@login_required
def close_cash(request):
    session = CashSession.objects.filter(status="OPEN").first()
    if not session: return redirect("cash_register")
    today = timezone.localdate()
    sales = Sale.objects.filter(sold_at=today, payment_method="CASH").aggregate(t=Sum("total"))["t"] or 0
    purchases = Purchase.objects.filter(purchased_at=today, paid_from_cash=True).aggregate(t=Sum("total"))["t"] or 0
    expenses = Expense.objects.filter(date=today, paid_from_cash=True).aggregate(t=Sum("amount"))["t"] or 0
    customer_payments = CustomerPayment.objects.filter(payment_date=today, payment_method="CASH").aggregate(t=Sum("amount"))["t"] or 0
    ins = session.movements.filter(movement_type="IN").aggregate(t=Sum("amount"))["t"] or 0
    outs = session.movements.filter(movement_type="OUT").aggregate(t=Sum("amount"))["t"] or 0
    expected = session.opening_amount + sales + customer_payments + ins - purchases - expenses - outs
    if request.method == "POST":
        counted=Decimal(request.POST["counted_amount"]); session.expected_amount=expected; session.counted_amount=counted; session.difference=counted-expected; session.status="CLOSED"; session.closed_at=timezone.now(); session.closed_by=request.user; session.save(); messages.success(request,"Caja cerrada correctamente."); return redirect("cash_register")
    return render(request,"stock/cash_close.html",{"session":session,"expected":expected})
