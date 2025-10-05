from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from .conexionsql import cargar_conexiones, get_connection
from .decorators import login_required
from .license_validator import validate_license
from moduls.sentencias import DatosGenerales

admin_bp = Blueprint("admin", __name__)

# ----------------------------------------------------------------------
# Vista principal de administración
# ----------------------------------------------------------------------
@admin_bp.route("/admin")
@login_required
def access_view():
    if session.get("usuario") != "sysadmin":
        return redirect(url_for("home"))

    conexiones = cargar_conexiones()
    datos_generales = {}

    for modulo in conexiones.keys():
        try:
            db_session = get_connection(modulo)
            if not db_session:
                datos_generales[modulo] = {"error": "No se pudo establecer sesión"}
                continue

            registros = db_session.query(DatosGenerales).all()
            headers = ["RAZONSOCIAL", "RFC", "DIRECCION1", "NUM_PROGRAMA", "CERTIFICACION1", "LICENCIA"]
            rows = [
                (d.RAZONSOCIAL, d.RFC, d.DIRECCION1, d.NUM_PROGRAMA, d.CERTIFICACION1, d.LICENCIA)
                for d in registros
            ]

            datos_generales[modulo] = {"headers": headers, "rows": rows}
        except Exception as e:
            datos_generales[modulo] = {"error": str(e)}
        finally:
            if 'db_session' in locals():
                db_session.close()

    return render_template("access.html", datos_generales=datos_generales)
# ----------------------------------------------------------------------
# Guardar datos en un módulo específico
# ----------------------------------------------------------------------
@admin_bp.route("/admin/guardar/<modulo>", methods=["POST"])
@login_required
def guardar_datos(modulo):
    if session.get("usuario") != "sysadmin":
        return redirect(url_for("home"))

    razon_social = request.form.get("razon_social")
    rfc = request.form.get("rfc")
    direccion1 = request.form.get("direccion1")
    num_programa = request.form.get("num_programa")
    certificacion1 = request.form.get("certificacion1")
    licencia = request.form.get("licencia")
    rfc_original = request.form.get("rfc_original")

    if not rfc or not licencia:
        flash("RFC y licencia son obligatorios.", "danger")
        return redirect(url_for("admin.access_view"))

    ok, info_or_msg = validate_license(licencia, expected_rfc=rfc, check_expiry=True)
    if not ok:
        flash(f"Licencia inválida: {info_or_msg}", "danger")
        return redirect(url_for("admin.access_view"))

    try:
        db_session = get_connection(modulo)
        if not db_session:
            flash(f"No se pudo establecer sesión para el módulo {modulo}", "danger")
            return redirect(url_for("admin.access_view"))

        registro = db_session.query(DatosGenerales).filter_by(RFC=rfc_original).first()
        if registro:
            registro.RAZONSOCIAL = razon_social
            registro.RFC = rfc
            registro.DIRECCION1 = direccion1
            registro.NUM_PROGRAMA = num_programa
            registro.CERTIFICACION1 = certificacion1
            registro.LICENCIA = licencia
        else:
            # Si no existe el registro, puedes crear uno nuevo o lanzar error según tu lógica
            nuevo_registro = DatosGenerales(
                RAZONSOCIAL=razon_social,
                RFC=rfc,
                DIRECCION1=direccion1,
                NUM_PROGRAMA=num_programa,
                CERTIFICACION1=certificacion1,
                LICENCIA=licencia
            )
            db_session.add(nuevo_registro)

        db_session.commit()
        flash({
            "tipo": "guardar",
            "rfc": rfc,
            "creado": info_or_msg.get("creado", "N/A"),
            "vence": info_or_msg.get("vence", "N/A")
        }, "success_license")

    except Exception as e:
        flash(f"Error al actualizar en {modulo}: {e}", "danger")
    finally:
        if 'db_session' in locals():
            db_session.close()

    return redirect(url_for("admin.access_view"))


@admin_bp.route("/admin/validar_licencia", methods=["POST"])
@login_required
def validar_licencia():
    if session.get("usuario") != "sysadmin":
        return redirect(url_for("home"))

    rfc = request.form.get("rfc")
    licencia = request.form.get("licencia")

    if not rfc or not licencia:
        flash("RFC y licencia son obligatorios para la validación.", "danger")
        return redirect(url_for("admin.access_view"))

    ok, info_or_msg = validate_license(licencia, expected_rfc=rfc, check_expiry=True)
    if not ok:
        flash(f"Licencia inválida: {info_or_msg}", "danger")
    else:
        flash({
            "tipo": "validar",
            "rfc": rfc,
            "vence": info_or_msg.get("vence", "N/A")
        }, "success_license")

    return redirect(url_for("admin.access_view"))

