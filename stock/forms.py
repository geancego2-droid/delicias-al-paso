from django import forms
from django.forms import inlineformset_factory
from .models import Product, Sale, SaleItem, Purchase, PurchaseItem, Expense, Customer, Supplier, Category

class SaleForm(forms.ModelForm):
    class Meta:
        model=Sale; fields=["customer","payment_method","paid","notes"]
class PurchaseForm(forms.ModelForm):
    class Meta:
        model=Purchase; fields=["supplier","invoice_number","purchased_at","paid_from_cash","notes"]; widgets={"purchased_at":forms.DateInput(attrs={"type":"date"})}
SaleItemFormSet=inlineformset_factory(Sale,SaleItem,fields=["product","quantity","unit_price"],extra=1,can_delete=True)
PurchaseItemFormSet=inlineformset_factory(Purchase,PurchaseItem,fields=["product","quantity","unit_cost"],extra=1,can_delete=True)
class ProductForm(forms.ModelForm):
    class Meta:
        model=Product; fields=["code","name","category","supplier","cost_price","sale_price","stock","minimum_stock","expiry_date","active"]
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "category", "description", "amount", "paid_from_cash"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
class CustomerForm(forms.ModelForm):
    class Meta:
        model=Customer; fields=["name","document","phone","address","credit_limit","notes"]
class SupplierForm(forms.ModelForm):
    class Meta:
        model=Supplier; fields=["name","ruc","phone","address","email","notes"]

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category; fields=["name"]
