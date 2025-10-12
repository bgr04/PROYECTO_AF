from flask import Flask, render_template
from flask import Blueprint, session, render_template
from .conexionsql import get_connection
rutas_usuario_bp = Blueprint("rutas", __name__)


@rutas_usuario_bp.route("/datos-generales")
def cat_datos_generales():
    return render_template('cat_DatosGenerales.html')

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