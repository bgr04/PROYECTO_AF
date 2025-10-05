import os
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from urllib.parse import quote_plus

# Ruta del archivo de conexiones
ARCHIVO_CONEXIONES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conexiones.txt")

# Diccionarios globales para engines y sesiones
_engines = {}
_sessions = {}

def cargar_conexiones():
    if not os.path.exists(ARCHIVO_CONEXIONES):
        raise FileNotFoundError(f"No se encontró el archivo {ARCHIVO_CONEXIONES}")

    config = configparser.ConfigParser()
    config.read(ARCHIVO_CONEXIONES)

    conexiones = {}
    for section in config.sections():
        # Leer parámetros de la sección
        params = config[section]

        driver = params.get("driver", "ODBC Driver 18 for SQL Server")
        server = params.get("server", "")
        database = params.get("database", "")
        uid = params.get("uid", "")
        pwd = params.get("pwd", "")
        trust_cert = params.get("TrustServerCertificate", "yes")
 
        driver_enc = quote_plus(driver)  # Codifica espacios y caracteres especiales

        connection_url = (
            f"mssql+pyodbc://{uid}:{pwd}@{server}/{database}"
            f"?driver={driver_enc}&TrustServerCertificate={trust_cert}"
        )

        conexiones[section] = connection_url

    return conexiones

def inicializar_engines():
    global _engines, _sessions
    conexiones = cargar_conexiones()
    for modulo, url in conexiones.items():
        engine = create_engine(url, fast_executemany=True)
        _engines[modulo] = engine
        _sessions[modulo] = scoped_session(sessionmaker(bind=engine))

def get_connection(modulo):
    if not _sessions:
        inicializar_engines()
    if modulo not in _sessions:
        raise Exception(f"No se encontró sesión para módulo '{modulo}'")
    try:
        return _sessions[modulo]()
    except Exception as e:
        if "Login failed" in str(e) or "authentication" in str(e).lower():
            from flask import flash
            flash("Usuario o contraseña incorrecta.", "auth_error")
        else:
            flash(f"Error general al conectar: {e}", "danger")
        return None

def close_session(modulo):
    if modulo in _sessions:
        _sessions[modulo].remove()