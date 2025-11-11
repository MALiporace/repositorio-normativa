import os
import pandas as pd
import dropbox
from datetime import datetime, timedelta, timezone

# === 1. Inicializar cliente de Dropbox ===
dbx = dropbox.Dropbox(
    app_key=os.environ.get("APP_KEY"),
    app_secret=os.environ.get("APP_SECRET"),
    oauth2_refresh_token=os.environ.get("REFRESH_TOKEN")
)

# === 2. Configuración general ===
log_path = "ejecuciones.log"
argentina_tz = timezone(timedelta(hours=-3))
timestamp = datetime.now(argentina_tz).strftime("%Y-%m-%d %H:%M:%S")

# === 3. Descargar el CSV maestro desde Dropbox ===
dropbox_maestro_path = "/Proyecto Repositorio Normativo/normas_boletin_maestro.csv"
local_maestro_path = "normas_boletin_maestro.csv"

ultimo_id = None

try:
    dbx.files_download_to_file(local_maestro_path, dropbox_maestro_path)
    print("✅ Archivo maestro descargado desde Dropbox.")
except Exception as e:
    print(f"⚠️ No se pudo descargar el maestro desde Dropbox: {e}")

# === 4. Leer el último ID si el archivo existe ===
if os.path.exists(local_maestro_path):
    try:
        df = pd.read_csv(local_maestro_path)
        cols = [c.lower() for c in df.columns]
        if not df.empty:
            if "id" in cols:
                ultimo_id = df[df.columns[cols.index("id")]].iloc[-1]
            elif "id_norma" in cols:
                ultimo_id = df[df.columns[cols.index("id_norma")]].iloc[-1]
        print(f"📄 Último ID detectado: {ultimo_id}")
    except Exception as e:
        print(f"⚠️ Error al leer el maestro: {e}")
else:
    print("⚠️ No se encontró el archivo maestro local.")

# === 5. Determinar línea del log ===
if ultimo_id:
    linea_log = f"[{timestamp}] Ejecución completada. Último ID procesado: {ultimo_id}\n"
else:
    linea_log = f"[{timestamp}] Ejecución completada. Sin publicaciones detectadas.\n"

# === 6. Escribir / agregar al log ===
with open(log_path, "a", encoding="utf-8") as f:
    f.write(linea_log)

# === 7. Subir log actualizado a Dropbox ===
try:
    with open(log_path, "rb") as f:
        dbx.files_upload(
            f.read(),
            "/logs/ejecuciones.log",
            mode=dropbox.files.WriteMode("overwrite")
        )
    print("✅ Log actualizado y subido exitosamente a Dropbox.")
except Exception as e:
    print(f"⚠️ Error al subir el log a Dropbox: {e}")
