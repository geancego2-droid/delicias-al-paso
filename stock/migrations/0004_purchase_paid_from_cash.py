from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("stock", "0003_customerpayment")]
    operations = [migrations.AddField(model_name="purchase", name="paid_from_cash", field=models.BooleanField(default=True, verbose_name="Pagado desde caja"))]
