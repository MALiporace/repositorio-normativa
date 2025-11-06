# -*- coding: utf-8 -*-

# === LIBRERÍAS ===
#!apt-get -qq update
#!apt-get -qq install -y firefox
#!wget -q https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz
#!tar -xzf geckodriver-v0.36.0-linux64.tar.gz
#!mv geckodriver /usr/local/bin/
#!chmod +x /usr/local/bin/geckodriver
#!pip install -q selenium bs4 google-generativeai dropbox

# === IMPORTS ===
import io
import random
import time
import re
import dropbox
import pandas as pd
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from google.generativeai import configure, GenerativeModel

# === CONFIGURACIÓN ===
APP_KEY = os.environ["APP_KEY"]
APP_SECRET = os.environ["APP_SECRET"]
REFRESH_TOKEN = os.environ["REFRESH_TOKEN"]

RUTA_ID_MATUTINA = "/Proyecto Repositorio Normativo/ultimo_id_norma_matutina.txt"
RUTA_ID_VESPERTINA = "/Proyecto Repositorio Normativo/ultimo_id_norma_vespertina.txt"
RUTA_MAESTRO = "/Proyecto Repositorio Normativo/normas_boletin_maestro.csv"
RUTA_HISTORICOS = "/Proyecto Repositorio Normativo/Historicos/"

configure(api_key=os.environ["GOOGLE_API_KEY"])
modelo_gemini = GenerativeModel("gemini-2.5-flash")

# === FUNCIONES DROPBOX ===
def get_dropbox_client():
    return dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=REFRESH_TOKEN
    )

def leer_ultimo_id(tipo):
    dbx = get_dropbox_client()
    ruta = RUTA_ID_MATUTINA if tipo == "matutina" else RUTA_ID_VESPERTINA
    try:
        _, res = dbx.files_download(ruta)
        return int(res.content.decode().strip())
    except Exception:
        # Si no existe el archivo, se asigna un valor base según el tipo
        return 333000 if tipo == "matutina" else 5957264

def guardar_ultimo_id(tipo, nuevo_id):
    dbx = get_dropbox_client()
    ruta = RUTA_ID_MATUTINA if tipo == "matutina" else RUTA_ID_VESPERTINA
    dbx.files_upload(f"{nuevo_id}".encode(), ruta, mode=dropbox.files.WriteMode("overwrite"))

# === FUNCIÓN GEMINI ===
def resumir_con_gemini(texto):
    if not texto or len(texto) < 50:
        return texto.strip()
    prompt = f"""
Sos un analista jurídico especializado en normas del Boletín Oficial Argentino.
Leé el siguiente texto normativo y redactá un resumen interpretativo en español,
claro, sintético y con lenguaje técnico-administrativo (no literario).

El resumen debe indicar brevemente:
- Qué tipo de disposición es (resolución, decreto, comunicación, etc.)
- Qué tema o materia regula.
- Cuál es el objeto o efecto principal.
- Si se menciona algún organismo o dependencia relevante.

Limite máximo: 100 palabras.

Texto original:
{texto.strip()}
"""
    try:
        respuesta = modelo_gemini.generate_content(prompt)
        resumen = respuesta.text.strip()
        if not resumen or len(resumen) < 20:
            resumen = texto[:400] + "..."
        elif len(resumen) > 600:
            resumen = resumen[:600] + "..."
        return resumen
    except Exception as e:
        print("?? Error al resumir con Gemini:", e)
        return texto[:600] + "..."

# === SELENIUM ===
def init_driver(headless=False):
    opts = Options()
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    opts.set_preference("general.useragent.override", ua)
    opts.set_preference("intl.accept_languages", "es-ES,es;q=0.9,en;q=0.8")
    opts.set_preference("dom.webdriver.enabled", False)
    opts.set_preference("useAutomationExtension", False)
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--width=1920")
    opts.add_argument("--height=1080")
    driver = webdriver.Firefox(options=opts)
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass
    return driver

# === SCRAPEO DE NORMA ===
def scrape_norma(driver, id_norma, fecha_base_yyyymmdd, tipo="matutina"):
    
    if tipo == "vespertina":
    url = f"https://www.boletinoficial.gov.ar/detalleAviso/primera/{id_norma}/{fecha_base_yyyymmdd}?suplemento=1"
else:
    url = f"https://www.boletinoficial.gov.ar/detalleAviso/primera/{id_norma}/{fecha_base_yyyymmdd}"

    driver.get(url)
    time.sleep(random.uniform(2, 4))

    html = driver.page_source
    if "cuerpoDetalleAviso" not in html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    titulo_div = soup.find("div", id="tituloDetalleAviso")
    cuerpo_div = soup.find("div", id="cuerpoDetalleAviso")

    if not titulo_div or not cuerpo_div:
        return None

    org = titulo_div.find("h1").get_text(strip=True) if titulo_div.find("h1") else ""
    norma = titulo_div.find("h2").get_text(strip=True) if titulo_div.find("h2") else ""
    extracto = titulo_div.find("h6").get_text(strip=True) if titulo_div.find("h6") else ""
    texto = cuerpo_div.get_text(separator=" ", strip=True)
    resumen = resumir_con_gemini(texto)

    return {
        "Organismo": org,
        "N° de Norma": norma,
        "Extracto": extracto,
        "Fecha": fecha_base_yyyymmdd,
        "ID": id_norma,
        "URL": url,
        "Texto": resumen
    }

# === SCRAPEO COMPLETO ===
def scrape_dia_completo(headless=False):
    hora_actual = datetime.now(timezone(timedelta(hours=-3))).hour
    tipo = "matutina" if hora_actual < 12 else "vespertina"

    fecha_base = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y%m%d")
    id_inicial = leer_ultimo_id(tipo) + 1

    print(f"?? Ejecutando edición {tipo.upper()} ({fecha_base}), desde ID {id_inicial}")
    driver = init_driver(headless=headless)

    data = []
    id_actual = id_inicial
    sin_resultados = 0
    limite = 400 if tipo == "matutina" else 800

    while sin_resultados < 30 and id_actual - id_inicial < limite:
        resultado = scrape_norma(driver, id_actual, fecha_base, tipo)
        if resultado:
            data.append(resultado)
            sin_resultados = 0
            print(f"? {id_actual}")
        else:
            sin_resultados += 1
            print(f"?? {id_actual} vacío ({sin_resultados}/30)")
        id_actual += 1
        time.sleep(random.uniform(0.8, 1.8))

    driver.quit()

    if not data:
        print("?? No se encontraron normas nuevas.")
        return

    df_nuevo = pd.DataFrame(data)
    dbx = get_dropbox_client()

    # === Cargar y actualizar maestro ===
    try:
        _, res = dbx.files_download(RUTA_MAESTRO)
        df_maestro = pd.read_csv(io.StringIO(res.content.decode("utf-8")))
        df_final = pd.concat([df_maestro, df_nuevo], ignore_index=True)
        df_final = df_final.drop_duplicates(subset=["ID"], keep="last")
    except dropbox.exceptions.ApiError:
        df_final = df_nuevo

    # === Generar CSV parcial ===
    hora_str = datetime.now(timezone(timedelta(hours=-3))).strftime("%H%M")
    nombre_parcial = f"normas_boletin_{fecha_base}_{tipo}_{hora_str}.csv"
    df_nuevo.to_csv(nombre_parcial, index=False, encoding="utf-8")

    # === Subir CSV parcial a carpeta Historicos ===
    ruta_dropbox_parcial = f"{RUTA_HISTORICOS}{nombre_parcial}"
    with open(nombre_parcial, "rb") as f:
        dbx.files_upload(f.read(), ruta_dropbox_parcial, mode=dropbox.files.WriteMode("overwrite"))
    print(f"?? CSV parcial subido a {ruta_dropbox_parcial}")

    # === Actualizar maestro ===
    with io.BytesIO() as buffer:
        df_final.to_csv(buffer, index=False, encoding="utf-8")
        buffer.seek(0)
        dbx.files_upload(buffer.read(), RUTA_MAESTRO, mode=dropbox.files.WriteMode("overwrite"))

    guardar_ultimo_id(tipo, id_actual - sin_resultados - 1)
    print(f"? {len(data)} normas nuevas ({tipo}). CSV maestro actualizado en Dropbox.")

# === EJECUTAR ===

scrape_dia_completo(headless=True)



