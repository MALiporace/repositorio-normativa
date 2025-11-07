import os
import dropbox

# Inicializar cliente de Dropbox
dbx = dropbox.Dropbox(
    app_key=os.environ.get("APP_KEY"),
    app_secret=os.environ.get("APP_SECRET"),
    oauth2_refresh_token=os.environ.get("REFRESH_TOKEN")
)

# Ruta local del log
log_path = "ejecuciones.log"

# Verificar existencia del archivo y crear uno vacío si no existe
if not os.path.exists(log_path):
    with open(log_path, "w") as f:
        f.write("⚠️ Log vacío: no se registraron eventos.\n")

# Subir a Dropbox
with open(log_path, "rb") as f:
    dbx.files_upload(
        f.read(),
        "/Proyecto Repositorio Normativo/logs/ejecuciones.log",
        mode=dropbox.files.WriteMode("overwrite")
    )

print("✅ Log subido exitosamente a Dropbox.")
