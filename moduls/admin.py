from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from .conexionsql import cargar_conexiones, get_connection
from .__init__ import login_required
from .license_validator import validate_license
from sqlalchemy import text 

admin_bp = Blueprint("admin", __name__)

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

            registros = db_session.execute(
            text("EXEC SP_DatosGenerales @accion = :accion"),
            {"accion": 1}).mappings().all()
            
            headers = [col for col in registros[0].keys() if col != 'DatosGeneralesKey'] if registros else []
            rows = [tuple(row.values()) for row in registros]

            datos_generales[modulo] = {"headers": headers, "rows": rows}
        
        except Exception as e:
            datos_generales[modulo] = {"error": str(e)}
        finally:
            if 'db_session' in locals():
                db_session.close()

    return render_template("access.html", datos_generales=datos_generales)


@admin_bp.route("/admin/guardar/<modulo>", methods=["POST"])
@login_required
def guardar_datos(modulo):
    if session.get("usuario") != "sysadmin":
        return redirect(url_for("home"))

    id_registro = request.form.get("id")
    print("ID recibido:", id_registro)

    rfc_original = request.form.get("rfc_original")
    rfc = request.form.get("RFCTaxId")
    razon_social = request.form.get("RazonSocial")
    calle = request.form.get("Calle")
    num_exterior = request.form.get("NumExterior")
    num_interior = request.form.get("NumInterior")
    colonia = request.form.get("Colonia")
    codigo_postal = request.form.get("CodigoPostal")
    municipio = request.form.get("Municipio")
    estado = request.form.get("Estado")
    pais = request.form.get("Pais")
    numero_programa = request.form.get("NumeroPrograma")
    certificacion = request.form.get("Certificacion")
    licencia = request.form.get("Licencia")

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

        result = db_session.execute(
            text("""
                EXEC SP_DatosGenerales 
                    @accion=:accion,
                    @DatosGeneralesKey=:DatosGeneralesKey,
                    @RFCTaxId=:RFCTaxId,
                    @RazonSocial=:RazonSocial,
                    @Calle=:Calle,
                    @NumExterior=:NumExterior,
                    @NumInterior=:NumInterior,
                    @Colonia=:Colonia,
                    @CodigoPostal=:CodigoPostal,
                    @Municipio=:Municipio,
                    @Estado=:Estado,
                    @Pais=:Pais,
                    @NumeroPrograma=:NumeroPrograma,
                    @Certificacion=:Certificacion,
                    @Licencia=:Licencia
            """),
            {
                "accion": 2,  # Acción de actualización
                "DatosGeneralesKey": id_registro,
                "RFCTaxId": rfc,
                "RazonSocial": razon_social,
                "Calle": calle,
                "NumExterior": num_exterior,
                "NumInterior": num_interior,
                "Colonia": colonia,
                "CodigoPostal": codigo_postal,
                "Municipio": municipio,
                "Estado": estado,
                "Pais": pais,
                "NumeroPrograma": numero_programa,
                "Certificacion": certificacion,
                "Licencia": licencia
            }
        )

        print("Resultado del SP:", result)
        
        db_session.commit()

        flash({
            "tipo": "guardar",
            "rfc": rfc,
            "creado": info_or_msg.get("creado", "N/A"),
            "vence": info_or_msg.get("vence", "N/A")
        }, "success_license")

    except Exception as e:
        db_session.rollback()  # Revertir cambios en caso de error
        flash(f"Error al actualizar en {modulo}: {e}", "danger")

    finally:
        if 'db_session' in locals():
            db_session.close()

    # Redirigir después de que todo haya sucedido
    return redirect(url_for("admin.access_view"))


@admin_bp.route("/admin/validar_licencia", methods=["POST"])
@login_required
def validar_licencia():
    if session.get("usuario") != "sysadmin":
        return redirect(url_for("home"))

    # Alinear con los nombres reales del formulario
    rfc = request.form.get("RFCTaxId")
    licencia = request.form.get("Licencia")

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
