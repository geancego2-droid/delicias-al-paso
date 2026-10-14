# Control de Stock — Almacén Paraguay

Base inicial de una aplicación web para gestión de almacén, en español y con montos en guaraníes. Funciona en Windows 10/11 durante desarrollo y puede desplegarse en un servidor para acceso remoto.

## Incluye en esta versión inicial
- Inicio de sesión y usuarios de Django.
- Panel con resumen de ventas registradas, gastos, valor del inventario y alertas de stock mínimo.
- Administración de productos, categorías, proveedores, clientes, compras, detalles de compra, ventas, detalles de venta, gastos y movimientos de stock.
- Base de datos SQLite para pruebas locales y PostgreSQL mediante `DATABASE_URL` para despliegue.
- Zona horaria `America/Asuncion`.

## Requisitos
- Python 3.11 o posterior.
- Windows 10/11.
- Internet solo para instalar dependencias y, en producción, acceder al servidor.

## Ejecutar localmente en Windows
1. Instalar Python desde https://www.python.org/downloads/ y marcar “Add Python to PATH”.
2. Extraer el ZIP a una carpeta, abrir PowerShell en esa carpeta.
3. Ejecutar:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

4. Abrir `http://127.0.0.1:8000/` e iniciar sesión. Para cargar los datos, abrir “Administrar módulos” o `http://127.0.0.1:8000/admin/`.

## Usuarios
Crear usuarios desde Administración → Usuarios. Asignar solo los permisos necesarios a cada cajero/encargado. No compartir la cuenta del administrador.

## Acceso remoto: importante
`runserver` es únicamente para desarrollo local y NO debe exponerse a Internet. Para el acceso desde distintos lugares, desplegar en un servidor con HTTPS, dominio, PostgreSQL, variables secretas y copias de seguridad. Configurar `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` y `DATABASE_URL`. No abrir directamente el puerto de desarrollo en el router.

## Estado y limitaciones
Este ZIP es una base funcional inicial, no un sistema contable certificado listo para operar sin pruebas. Los modelos de compra/venta y sus detalles están preparados para registro desde el administrador, pero la contabilización transaccional automática (descontar/aumentar stock al guardar detalles), control completo de caja/crédito, reportes exportables y balance formal todavía requieren implementación y pruebas. No usar para operaciones reales hasta completar esas validaciones, probar copias de seguridad y revisar la contabilidad con un profesional local.
