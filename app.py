from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from moduls.login import login_bp
from moduls.dashboard import dashboard_bp
from moduls.conexionsql import cargar_conexiones
from moduls.__init__ import login_required, login_required_ajax
from moduls.admin import admin_bp 
from moduls.rutas_usuario import rutas_usuario_bp

app = Flask(__name__)
app.secret_key = "jKJwELCx2u3eUS6x4cZyCC1dYNOql66Wf1AlDVG2R8YS8hQ8TEQVkhp2rV7DBuqFAXwdVLfMUd7w5okeVJcLfgeFbaOIAA=="

# Registrar los blueprints
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(rutas_usuario_bp)


@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("login.html")

@app.route("/get_modulos")
def get_modulos():
    """Devuelve la lista de bases de datos disponibles para el usuario"""
    usuario = request.args.get("usuario")
    if not usuario:
        return jsonify({"bases": []})

    conexiones = cargar_conexiones()
    bases = [{"display_name": modulo} for modulo in conexiones.keys()]
    return jsonify({"bases": bases})

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
