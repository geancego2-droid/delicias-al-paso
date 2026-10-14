from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .models import Customer, CustomerPayment, Sale
from django import forms

class PaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerPayment
        fields = ['amount','payment_method','payment_date','notes']
        widgets = {'payment_date': forms.DateInput(attrs={'type':'date'})}

@login_required
@require_http_methods(['GET','POST'])
def customer_payment(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    debt = sum((s.balance_due for s in Sale.objects.filter(customer=customer)), 0)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['amount'] > debt:
                form.add_error('amount', f'El pago no puede superar la deuda actual de Gs. {debt:,.0f}.')
            else:
                payment=form.save(commit=False); payment.customer=customer; payment.created_by=request.user; payment.save()
                messages.success(request, f'Pago de Gs. {payment.amount:,.0f} registrado.')
                return redirect('customers')
    else: form=PaymentForm()
    return render(request,'stock/customer_payment.html',{'customer':customer,'debt':debt,'form':form})
