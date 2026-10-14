# Despliegue seguro — DELICIAS AL PASO

## Estado
- Proyecto Django y módulo stock ya existen.
- Las migraciones 0001–0003 se encuentran aplicadas en la base local.
- El archivo `render.yaml` describe un servicio Django y PostgreSQL.
- No publicar la base local `db.sqlite3`, archivos `.env`, usuarios ni datos comerciales.
- El sistema no se considera publicado ni listo para operar con datos reales hasta completar la lista de seguridad.

## Requisitos para Render
1. Tener un repositorio privado Git en GitHub, GitLab o Bitbucket.
2. Subir solamente el código y los archivos de configuración; verificar que `.gitignore` esté aplicado.
3. Añadir método de pago en Render si lo exige el plan elegido. La creación de PostgreSQL fue rechazada con HTTP 402 por falta de información de pago.
4. Crear recursos aplicando el Blueprint `render.yaml` desde el Dashboard.
5. Revisar costos, región y planes antes de aplicar; no se han creado servicios ni bases de datos.
6. Esperar a que el primer despliegue termine, luego crear una cuenta de administrador con contraseña fuerte.
7. Configurar copias de seguridad y hacer una prueba de restauración antes de migrar datos de negocio.

## Variables de entorno previstas
- `DJANGO_DEBUG=0`
- `DJANGO_SECRET_KEY`: generada por el proveedor, no compartir ni versionar.
- `DJANGO_ALLOWED_HOSTS`: host final real.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: URL HTTPS final.
- `DATABASE_URL`: URL interna de PostgreSQL administrado por Render.

## Comandos en el servicio
- Construcción: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Arranque: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`

## Comprobaciones pendientes
- Configurar hosting y PostgreSQL.
- Confirmar el hostname real y los parámetros CSRF.
- Revisar el cálculo de caja, cobros y reportes con pruebas funcionales antes de producción.
- Preparar usuarios individuales y permisos por rol.
- Exportar y revisar un respaldo consistente antes de cualquier importación.
- Probar el inicio de sesión, alta de venta, compra, gasto y ajuste de stock en dos navegadores móviles.
- Mantener el servidor de desarrollo local fuera de Internet.

Nunca compartir claves, enlaces privados de base de datos ni credenciales en el repositorio.
