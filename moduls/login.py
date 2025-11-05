from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from datetime import datetime
from moduls.conexionsql import get_connection
from moduls.sentencias import Usuario, DatosGenerales
from moduls.license_validator import validate_license

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

@login_bp.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario", "").strip()
    password = request.form.get("password", "").strip()
    modulo = request.form.get("modulo", "").strip()

    if usuario == "sysadmin" and password == "8PiE?0YDuYXT_8Jz":
        session["usuario"] = "sysadmin"
        session["is_sysadmin"] = True
        session["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return redirect(url_for("admin.access_view"))
    
    if not usuario or not password or not modulo:
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for("home"))

    try:
        db_session = get_connection(modulo)
        if db_session is None:
            flash("No se pudo establecer sesión con la base de datos", "danger")
            return redirect(url_for("home"))

        user = db_session.query(Usuario).filter_by(USUARIO=usuario).first()
        if not user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("home"))

        if user.ACTIVO != 1:
            flash("El usuario está inactivo", "warning")
            return redirect(url_for("home"))

        if user.CONTRASENA != password:
            flash("Contraseña incorrecta", "danger")
            return redirect(url_for("home"))

        # Guardar sesión
        session["usuario"] = user.USUARIO
        session["modulo"] = modulo
        session["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Validar licencia del módulo
        datos_generales = db_session.query(DatosGenerales).first()
        if not datos_generales:
            flash("No se encontraron datos generales para esta base. Contacta al administrador.", "danger")
            return redirect(url_for("login.login"))

        rfc = datos_generales.RFCTaxId
        licencia = datos_generales.Licencia

        if not licencia:
            flash("No se encontró licencia válida. Contacta al administrador.", "danger")
            return redirect(url_for("login.login"))
        
        ok, info = validate_license(licencia, expected_rfc=rfc, check_expiry=True)
        if not ok:
            flash(f"⚠️ Licencia inválida o expirada para {rfc}. Contacta al administrador.", "warning")
            return redirect(url_for("login.login"))

        # Guardar RFC del usuario autenticado
        session["rfc_usuario"] = rfc

        flash("Inicio de sesión exitoso", "success")
        return redirect(url_for("dashboard.dashboard"))

    except Exception as e:
        error_msg = str(e).lower()
        if "login failed" in error_msg or "authentication" in error_msg:
            flash("Usuario o contraseña incorrecta", "auth_error")
        else:
            flash(f"Error de conexión: {e}", "danger")
        return redirect(url_for("login.login"))

    finally:
        if 'db_session' in locals():
            db_session.close()


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("home"))


