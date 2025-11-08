# descargar_log_dropbox.py
import os, dropbox

dbx = dropbox.Dropbox(
    app_key=os.environ.get("APP_KEY"),
    app_secret=os.environ.get("APP_SECRET"),
    oauth2_refresh_token=os.environ.get("REFRESH_TOKEN")
)

try:
    dbx.files_download_to_file("ejecuciones.log", "/logs/ejecuciones.log")
    print("✅ Log previo descargado.")
except dropbox.exceptions.ApiError:
    print("⚠️ No se encontró log previo en Dropbox.")
