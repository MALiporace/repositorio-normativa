import os
import dropbox
from datetime import datetime, timedelta, timezone

# Inicializar cliente de Dropbox
dbx = dropbox.Dropbox(
    app_key=os.environ.get("APP_KEY"),
    app_secret=os.environ.get("APP_SECRET"),
    oauth2_refresh_token=os.environ.get("REFRESH_TOKEN")
)

# 🗂 Ruta local del log
log_path = "ejecuciones.log"

# 🕒 Ajuste horario a Buenos Aires (UTC-3)
argentina_tz = timezone(timedelta(hours=-3))
timestamp = datetime.now(argentina_tz).strftime("%Y-%m-%d %H:%M:%S")

# 🧩 Supongamos que tenés el último ID en una variable llamada `ultimo_id`
# Si el valor lo obtenés dinámicamente en otra parte del script, solo asegurate de tenerlo disponible acá.
# 🕒 Registrar fecha y hora de la ejecución
timestamp = datetime.now(argentina_tz).strftime("%Y-%m-%d %H:%M:%S")

# 🧩 Determinar qué mensaje dejar en el log
if 'ultimo_id' in locals() and ultimo_id is not None:
    linea_log = f"[{timestamp}] Ejecución completada. Último ID procesado: {ultimo_id}\n"
else:
    linea_log = f"[{timestamp}] Ejecución completada. Sin publicaciones detectadas.\n"

# 📝 Escribir o agregar al log existente
with open(log_path, "a", encoding="utf-8") as f:
    f.write(linea_log)


# 📝 Escribir o agregar al log existente
with open(log_path, "a", encoding="utf-8") as f:
    f.write(linea_log)

# ☁️ Subir versión consolidada al Dropbox
with open(log_path, "rb") as f:
    dbx.files_upload(
        f.read(),
        "/logs/ejecuciones.log",  # ruta relativa dentro del App Folder
        mode=dropbox.files.WriteMode("overwrite")
    )

print("✅ Log actualizado y subido exitosamente a Dropbox.")

