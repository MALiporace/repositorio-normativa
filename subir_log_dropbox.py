import os
import dropbox

dbx = dropbox.Dropbox(
    app_key=os.environ.get("APP_KEY"),
    app_secret=os.environ.get("APP_SECRET"),
    oauth2_refresh_token=os.environ.get("REFRESH_TOKEN")
)

with open("ejecuciones.log", "rb") as f:
    dbx.files_upload(
        f.read(),
        "/Proyecto Repositorio Normativo/logs/ejecuciones.log",
        mode=dropbox.files.WriteMode("overwrite")
    )
