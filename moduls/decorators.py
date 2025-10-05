from functools import wraps
from flask import session, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta

LIMITE_INACTIVIDAD = timedelta(minutes=10)

def session_expired():
    last_active = session.get('last_active')
    if last_active:
        try:
            last_active_dt = datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_active_dt > LIMITE_INACTIVIDAD:
                return True
        except Exception:
            return True
    else:
        return True
    return False # Si no hay marca de tiempo, tratamos como expirada

def update_last_active():
    session['last_active'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debes iniciar sesión para continuar.', 'auth_error')
            return redirect(url_for('login.login'))

        # Verifica si la sesión expiró
        if session_expired():
            session.clear()  # Limpia la sesión
            flash('Tu sesión ha expirado por inactividad.', 'warning')
            return redirect(url_for('login.login'))

        # Actualiza el último acceso
        update_last_active()

        return f(*args, **kwargs)
    return decorated_function

def login_required_ajax(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'error': 'Sesión expirada'}), 401
        return f(*args, **kwargs)
    return decorated_function
