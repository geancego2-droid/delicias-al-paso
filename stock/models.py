from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

class Category(Timestamped):
    name = models.CharField("Nombre", max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta: verbose_name = "Categoría"; verbose_name_plural = "Categorías"; ordering = ["name"]

class Supplier(Timestamped):
    name=models.CharField("Nombre / Razón social",max_length=180); ruc=models.CharField("RUC",max_length=30,blank=True); phone=models.CharField("Teléfono",max_length=50,blank=True); address=models.CharField("Dirección",max_length=220,blank=True); email=models.EmailField("Correo",blank=True); notes=models.TextField("Observaciones",blank=True)
    def __str__(self): return self.name
    class Meta: verbose_name="Proveedor"; verbose_name_plural="Proveedores"; ordering=["name"]

class Customer(Timestamped):
    name=models.CharField("Nombre",max_length=180); document=models.CharField("CI / RUC",max_length=30,blank=True); phone=models.CharField("Teléfono",max_length=50,blank=True); address=models.CharField("Dirección",max_length=220,blank=True); credit_limit=models.DecimalField("Límite de crédito (Gs.)",max_digits=14,decimal_places=0,default=0,validators=[MinValueValidator(0)]); notes=models.TextField("Observaciones",blank=True)
    def __str__(self): return self.name
    class Meta: verbose_name="Cliente"; verbose_name_plural="Clientes"; ordering=["name"]

class Product(Timestamped):
    code=models.CharField("Código / código de barras",max_length=80,unique=True); name=models.CharField("Producto",max_length=180); category=models.ForeignKey(Category,verbose_name="Categoría",on_delete=models.SET_NULL,null=True,blank=True); supplier=models.ForeignKey(Supplier,verbose_name="Proveedor habitual",on_delete=models.SET_NULL,null=True,blank=True); cost_price=models.DecimalField("Costo unitario (Gs.)",max_digits=14,decimal_places=0,validators=[MinValueValidator(0)]); sale_price=models.DecimalField("Precio de venta (Gs.)",max_digits=14,decimal_places=0,validators=[MinValueValidator(0)]); stock=models.IntegerField("Stock actual",default=0,validators=[MinValueValidator(0)]); minimum_stock=models.IntegerField("Stock mínimo",default=5,validators=[MinValueValidator(0)]); expiry_date=models.DateField("Vencimiento (opcional)",null=True,blank=True); active=models.BooleanField("Activo",default=True)
    def __str__(self): return f"{self.code} — {self.name}"
    @property
    def stock_value(self): return self.stock*self.cost_price
    @property
    def low_stock(self): return self.stock<=self.minimum_stock
    class Meta: verbose_name="Producto"; verbose_name_plural="Productos"; ordering=["name"]

class Purchase(Timestamped):
    supplier=models.ForeignKey(Supplier,verbose_name="Proveedor",on_delete=models.PROTECT); invoice_number=models.CharField("N.º de factura / comprobante",max_length=80,blank=True); purchased_at=models.DateField("Fecha de compra",default=timezone.localdate); total=models.DecimalField("Total (Gs.)",max_digits=16,decimal_places=0,default=0); paid_from_cash=models.BooleanField("Pagado desde caja",default=True); notes=models.TextField("Observaciones",blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self): return f"Compra #{self.pk} - {self.supplier}"
    class Meta: verbose_name="Compra"; verbose_name_plural="Compras"; ordering=["-purchased_at","-id"]

class PurchaseItem(Timestamped):
    purchase=models.ForeignKey(Purchase,verbose_name="Compra",on_delete=models.CASCADE,related_name="items"); product=models.ForeignKey(Product,verbose_name="Producto",on_delete=models.PROTECT); quantity=models.PositiveIntegerField("Cantidad"); unit_cost=models.DecimalField("Costo unitario (Gs.)",max_digits=14,decimal_places=0,validators=[MinValueValidator(0)])
    def __str__(self): return f"{self.product} x {self.quantity}"
    @property
    def subtotal(self): return self.quantity*self.unit_cost

class Sale(Timestamped):
    PAYMENT_CHOICES=[("CASH","Efectivo"),("TRANSFER","Transferencia"),("CARD","Tarjeta"),("CREDIT","Fiado / crédito"),("OTHER","Otro")]
    customer=models.ForeignKey(Customer,verbose_name="Cliente",on_delete=models.SET_NULL,null=True,blank=True); sold_at=models.DateField("Fecha de venta",default=timezone.localdate); payment_method=models.CharField("Medio de pago",max_length=12,choices=PAYMENT_CHOICES,default="CASH"); total=models.DecimalField("Total (Gs.)",max_digits=16,decimal_places=0,default=0); paid=models.DecimalField("Pagado (Gs.)",max_digits=16,decimal_places=0,default=0); notes=models.TextField("Observaciones",blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self): return f"Venta #{self.pk} - Gs. {self.total}"
    @property
    def balance_due(self): return max(self.total-self.paid, 0)
    @property
    def is_credit(self): return self.payment_method == "CREDIT" or self.balance_due > 0

class SaleItem(Timestamped):
    sale=models.ForeignKey(Sale,verbose_name="Venta",on_delete=models.CASCADE,related_name="items"); product=models.ForeignKey(Product,verbose_name="Producto",on_delete=models.PROTECT); quantity=models.PositiveIntegerField("Cantidad"); unit_price=models.DecimalField("Precio unitario (Gs.)",max_digits=14,decimal_places=0,validators=[MinValueValidator(0)]); unit_cost=models.DecimalField("Costo unitario al vender (Gs.)",max_digits=14,decimal_places=0,validators=[MinValueValidator(0)])
    @property
    def subtotal(self): return self.quantity*self.unit_price
    @property
    def gross_profit(self): return self.quantity*(self.unit_price-self.unit_cost)

class CustomerPayment(Timestamped):
    customer=models.ForeignKey(Customer,verbose_name='Cliente',on_delete=models.PROTECT,related_name='payments')
    amount=models.DecimalField('Importe (Gs.)',max_digits=16,decimal_places=0,validators=[MinValueValidator(1)])
    payment_method=models.CharField('Medio de pago',max_length=12,choices=Sale.PAYMENT_CHOICES,default='CASH')
    payment_date=models.DateField('Fecha',default=timezone.localdate)
    notes=models.CharField('Observaciones',max_length=220,blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self): return f'Pago de {self.customer} - Gs. {self.amount}'

class Expense(Timestamped):
    CATEGORY_CHOICES=[("RENT","Alquiler"),("POWER","Electricidad"),("SALARY","Salarios"),("TRANSPORT","Transporte"),("TAX","Impuestos"),("OTHER","Otros")]
    date=models.DateField("Fecha",default=timezone.localdate); category=models.CharField("Categoría",max_length=20,choices=CATEGORY_CHOICES,default="OTHER"); description=models.CharField("Descripción",max_length=220); amount=models.DecimalField("Importe (Gs.)",max_digits=14,decimal_places=0,validators=[MinValueValidator(1)]); paid_from_cash=models.BooleanField("Pagado de caja",default=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self): return f"{self.description} - Gs. {self.amount}"

class StockMovement(Timestamped):
    TYPES=[("IN","Entrada"),("OUT","Salida"),("ADJUST","Ajuste")]
    product=models.ForeignKey(Product,verbose_name="Producto",on_delete=models.PROTECT); movement_type=models.CharField("Tipo",max_length=8,choices=TYPES); quantity=models.IntegerField("Cantidad (+/-)"); reason=models.CharField("Motivo",max_length=220); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)

class CashSession(models.Model):
    STATUS=[("OPEN","Abierta"),("CLOSED","Cerrada")]
    opened_at=models.DateTimeField(auto_now_add=True); closed_at=models.DateTimeField(null=True,blank=True); opening_amount=models.DecimalField(max_digits=16,decimal_places=0,default=0); counted_amount=models.DecimalField(max_digits=16,decimal_places=0,null=True,blank=True); expected_amount=models.DecimalField(max_digits=16,decimal_places=0,default=0); difference=models.DecimalField(max_digits=16,decimal_places=0,default=0); status=models.CharField(max_length=8,choices=STATUS,default="OPEN"); opened_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name="cash_openings"); closed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="cash_closings"); notes=models.TextField(blank=True)
    class Meta: ordering=["-opened_at"]

class CashMovement(models.Model):
    TYPES=[("IN","Ingreso"),("OUT","Egreso")]
    session=models.ForeignKey(CashSession,on_delete=models.PROTECT,related_name="movements"); movement_type=models.CharField(max_length=3,choices=TYPES); amount=models.DecimalField(max_digits=16,decimal_places=0); description=models.CharField(max_length=220); created_at=models.DateTimeField(auto_now_add=True); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return f"{self.get_movement_type_display()} Gs. {self.amount}"
