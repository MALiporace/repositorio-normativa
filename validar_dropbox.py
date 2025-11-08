import os
import dropbox

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

print("🔍 Verificando credenciales...")

if not all([APP_KEY, APP_SECRET, REFRESH_TOKEN]):
    print("❌ Faltan variables de entorno. Verificá APP_KEY, APP_SECRET o REFRESH_TOKEN.")
    exit(1)

try:
    dbx = dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=REFRESH_TOKEN
    )

    cuenta = dbx.users_get_current_account()
    print(f"✅ Conexión exitosa como: {cuenta.name.display_name} ({cuenta.email})")

except dropbox.exceptions.AuthError as e:
    print("❌ Error de autenticación con Dropbox:")
    print(e)
    exit(1)

except Exception as e:
    print("❌ Error inesperado:")
    print(e)
    exit(1)
