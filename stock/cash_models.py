from django.conf import settings
from django.db import models
from django.utils import timezone

class CashSession(models.Model):
    STATUS = [("OPEN", "Abierta"), ("CLOSED", "Cerrada")]
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_amount = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    counted_amount = models.DecimalField(max_digits=16, decimal_places=0, null=True, blank=True)
    expected_amount = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    difference = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    status = models.CharField(max_length=8, choices=STATUS, default="OPEN")
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="cash_openings")
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="cash_closings")
    notes = models.TextField(blank=True)
    class Meta: ordering = ["-opened_at"]

class CashMovement(models.Model):
    TYPES = [("IN", "Ingreso"), ("OUT", "Egreso")]
    session = models.ForeignKey(CashSession, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=3, choices=TYPES)
    amount = models.DecimalField(max_digits=16, decimal_places=0)
    description = models.CharField(max_length=220)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    class Meta: ordering = ["-created_at"]

    def __str__(self): return f"{self.get_movement_type_display()} Gs. {self.amount}"
