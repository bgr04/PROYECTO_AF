from flask import Blueprint, session, render_template
from .decorators import login_required
from datetime import datetime, date
from .conexionsql import get_connection
from .license_validator import validate_license
from moduls.sentencias import DatosGenerales
dashboard_bp = Blueprint("dashboard", __name__)

def obtener_dias_restantes_licencia(licencia_token: str) -> int:
    ok, info = validate_license(licencia_token, check_expiry=False)
    if not ok:
        return None
    fecha_vence_str = info.get("vence")  # Ej: "2025-10-30 23:59:59"
    if not fecha_vence_str:
        return None
    try:
        fecha_vence = datetime.strptime(fecha_vence_str, "%Y-%m-%d %H:%M:%S")
        hoy = date.today()
        delta = fecha_vence - hoy
        dias_restantes = max(delta.days, 0)
        return dias_restantes
    except Exception:
        return None

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    usuario = session.get("usuario")
    modulo = session.get("modulo")
    rfc = None
    rfc = session.get("rfc_usuario")  # Ajusta según tu sistema

    dias_restantes = None
    if rfc and modulo:
        try:
            db_session = get_connection(modulo)
            if db_session:
                datos = db_session.query(DatosGenerales).filter_by(RFC=rfc).first()
                if datos and datos.LICENCIA:
                    licencia_token = datos.LICENCIA
                    dias_restantes = obtener_dias_restantes_licencia(licencia_token)
        except Exception as e:
            print(f"Error al obtener licencia: {e}")
            dias_restantes = None
        finally:
            if 'db_session' in locals():
                db_session.close()

    return render_template("dashboard.html", usuario=usuario, modulo=modulo, dias_restantes=dias_restantes)
