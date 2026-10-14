from django.urls import path
from . import views
from .cash_views import cash_register,cash_movement,close_cash
from .customer_views import customer_payment
from .report_views import reports
urlpatterns=[path('',views.dashboard,name='stock-dashboard'),path('venta/nueva/',views.new_sale,name='new_sale'),path('compra/nueva/',views.new_purchase,name='new_purchase'),path('productos/',views.products,name='products'),path('productos/nuevo/',views.new_product,name='new_product'),path('clientes/',views.customers,name='customers'),path('clientes/<int:customer_id>/pago/',customer_payment,name='customer_payment'),path('reportes/',reports,name='reports'),path('caja/',cash_register,name='cash_register'),path('caja/movimiento/',cash_movement,name='cash_movement'),path('caja/cerrar/',close_cash,name='close_cash'),path('gastos/nuevo/',views.new_expense,name='new_expense')]
