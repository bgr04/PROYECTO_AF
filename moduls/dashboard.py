from flask import Blueprint, session, render_template
from .__init__ import login_required
from datetime import datetime, date
from .conexionsql import get_connection
from .license_validator import validate_license
from moduls.sentencias import DatosGenerales
dashboard_bp = Blueprint("dashboard", __name__)


def obtener_dias_restantes_licencia(licencia_token: str) -> int:    
    ok, info = validate_license(licencia_token, check_expiry=False)

    if not ok:   
        return None

    fecha_vence_str = info.get("vence")
    if not fecha_vence_str:
        return None
    try:
        fecha_vence = datetime.strptime(fecha_vence_str, "%Y-%m-%d %H:%M:%S")
        hoy = date.today()
        delta = fecha_vence.date() - hoy
        dias_restantes = max(delta.days, 0)
        return dias_restantes
    except Exception as e:
        # print(f"[ERROR] Error al calcular días restantes: {e}")
        return None

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    usuario = session.get("usuario")
    modulo = session.get("modulo")
    rfc = session.get("rfc_usuario")

    dias_restantes = None
    licencia_token = None

    if rfc and modulo:
        try:
            db_session = get_connection(modulo)
            if db_session:
                # Usamos RFCTaxId en lugar de RFC
                datos = db_session.query(DatosGenerales).filter_by(RFCTaxId=rfc).first()

                if datos and datos.Licencia:  # Usamos Licencia en lugar de LICENCIA
                    licencia_token = datos.Licencia
                    dias_restantes = obtener_dias_restantes_licencia(licencia_token)
                else:
                    print(f"[DEBUG] No se encontró licencia para RFC {rfc} en {modulo}")
            else:
                print(f"[ERROR] No se pudo conectar al módulo {modulo}")
        except Exception as e:
            print(f"[ERROR] Falló la consulta de datos generales: {e}")
            dias_restantes = None
        finally:
            if 'db_session' in locals():
                db_session.close()
    else:
        print("[DEBUG] RFC o módulo no disponibles en sesión")

    return render_template(
        "dashboard.html",
        usuario=usuario,
        modulo=modulo,
        dias_restantes=dias_restantes,
        licencia=licencia_token
    )
