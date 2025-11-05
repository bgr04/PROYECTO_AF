from flask import Blueprint, session, render_template, redirect, url_for, flash, request, jsonify
from .conexionsql import get_connection
from .__init__ import login_required
from moduls.sentencias import DatosGenerales
from sqlalchemy import text

rutas_usuario_bp = Blueprint("rutas", __name__)

@rutas_usuario_bp.route("/datos-generales")
@login_required
def cat_datos_generales():
    usuario = session.get("usuario")
    modulo = session.get("modulo")

    if not usuario or not modulo:
        flash("Sesión inválida o expirada. Inicia sesión nuevamente.", "danger")
        return redirect(url_for("login.login"))

    try:
        db_session = get_connection(modulo)
        if not db_session:
            flash("No se pudo establecer conexión con la base de datos.", "danger")
            return redirect(url_for("dashboard.dashboard"))

        # Obtener los datos generales (de la tabla del módulo del usuario)
        datos = db_session.query(DatosGenerales).first()
        if not datos:
            flash("No se encontraron datos generales para este módulo.", "warning")
            return redirect(url_for("dashboard.dashboard"))

        # Convertir en diccionario y eliminar la licencia
        data = {
            "DatosGeneralesKey": datos.DatosGeneralesKey,
            "RFCTaxId": datos.RFCTaxId,
            "RazonSocial": datos.RazonSocial,
            "Calle": datos.Calle,
            "NumExterior": datos.NumExterior,
            "NumInterior": datos.NumInterior,
            "Colonia": datos.Colonia,
            "CodigoPostal": datos.CodigoPostal,
            "Municipio": datos.Municipio,
            "Estado": datos.Estado,
            "Pais": datos.Pais,
            "NumeroPrograma": datos.NumeroPrograma,
            "Certificacion": datos.Certificacion,
            "Licencia": datos.Licencia
        }

        return render_template("cat_DatosGenerales.html", usuario=usuario, modulo=modulo, datos=data)

    except Exception as e:
        flash(f"Error al obtener los datos: {e}", "danger")
        return redirect(url_for("dashboard.dashboard"))
    finally:
        if 'db_session' in locals():
            db_session.close()

@rutas_usuario_bp.route("/datos-generales/actualizar", methods=["POST"])
@login_required
def actualizar_datos_generales():
    usuario = session.get("usuario")
    modulo = session.get("modulo")

    if not usuario or not modulo:
        return jsonify({"status": "error", "message": "Sesión inválida o expirada."})

    try:
        db_session = get_connection(modulo)
        if not db_session:
            return jsonify({"status": "error", "message": "No se pudo establecer conexión con la base de datos."})

        # Obtener los datos del formulario
        id_registro = request.form.get("DatosGeneralesKey")
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
        licencia = request.form.get("Licencia")  # Aunque no se actualiza, se puede obtener si es necesario

        # Validación básica (si es necesario)
        if not rfc:
            return jsonify({"status": "error", "message": "El RFC es obligatorio."})

        # Ejecutar el procedimiento almacenado para actualizar los datos
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

        db_session.commit()

        # Responder con éxito
        return jsonify({
            "status": "success",
            "message": "Datos actualizados correctamente.",
            "rfc": rfc
        })

    except Exception as e:
        if 'db_session' in locals():
            db_session.rollback()
        return jsonify({"status": "error", "message": f"Error al actualizar: {e}"})

    finally:
        if 'db_session' in locals():
            db_session.close()




@rutas_usuario_bp.route("/cat_usuarios")
def cat_usuarios():
    return render_template('cat_Usuarios.html')

@rutas_usuario_bp.route("/cat_proveedores")
def cat_proveedores():
    return render_template('cat_Proveedores.html')

@rutas_usuario_bp.route("/cat_clientes")
def cat_clientes():
    return render_template('cat_Clientes.html')

@rutas_usuario_bp.route("/cat_categoria")
def cat_categoria():
    return render_template('cat_Categoria.html')

@rutas_usuario_bp.route("/cat_departamento")
def cat_departamento():
    return render_template('cat_Departamento.html')

@rutas_usuario_bp.route("/cat_tipoEquipos")
def cat_tipoEquipos():
    return render_template('cat_TipoEquipo.html')

@rutas_usuario_bp.route("/cat_estado")
def cat_estado():
    return render_template('cat_Estado.html')

@rutas_usuario_bp.route("/cat_archivos")
def cat_archivos():
    return render_template('cat_Archivos.html')

@rutas_usuario_bp.route("/cat_activoFijo")
def cat_activoFijo():
    return render_template('cat_ActivoFijo.html')



@rutas_usuario_bp.route("/controlAF_E")
def controlAF_E():
    return render_template('controlAF_Entradas.html')

@rutas_usuario_bp.route("/controlAF_S")
def controlAF_S():
    return render_template('controlAF_Salidas.html')



@rutas_usuario_bp.route("/expedienteD")
def expedienteD():
    return render_template('expedienteDigital.html')



@rutas_usuario_bp.route("/reporteG")
def reporteG():
    return render_template('reporte_General.html')

@rutas_usuario_bp.route("/reporteED")
def reporteED():
    return render_template('reporte_ED.html')