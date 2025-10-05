import os
from pathlib import Path
from datetime import datetime, date
from typing import Tuple, Union, Dict
import jwt
from cryptography.hazmat.primitives import serialization
from pathlib import Path

# ----------------------------
# Configuración
# ----------------------------
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ruta al archivo public.pem en la raíz
PUBLIC_KEY_PATH = os.path.join(BASEDIR, "public.pem")
# PUBLIC_KEY_PATH = "public.pem"
JWT_ALGORITHM = "RS256"

# ----------------------------
# Cargar clave pública
# ----------------------------
def load_public_key(path: str = PUBLIC_KEY_PATH) -> bytes:
    return Path(path).read_bytes()

# ----------------------------
# Validar token JWT
# ----------------------------
def validate_license(token: str, expected_rfc: str = None, check_expiry: bool = True) -> Tuple[bool, Union[Dict[str, str], str]]:
    if not token:
        return False, "Token vacío"

    try:
        public_key = load_public_key()
        payload = jwt.decode(token, public_key, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return False, "Licencia expirada"
    except jwt.InvalidTokenError as e:
        return False, f"Token inválido: {e}"

    # Validar RFC si se espera
    if expected_rfc:
        rfc_token = payload.get("rfc", "").strip().upper()
        rfc_esperado = expected_rfc.strip().upper()
        if rfc_token != rfc_esperado:
            return False, f"El RFC de la licencia ('{rfc_token}') no corresponde al RFC registrado: '{rfc_esperado}'"

    # Validar expiración si aplica
    if check_expiry:
        try:
            exp_ts = payload.get("exp")
            exp_date = datetime.fromtimestamp(exp_ts).date()
            if exp_date < date.today():
                return False, f"Licencia expirada desde {exp_date.strftime('%Y-%m-%d')}"
        except Exception:
            return False, "Error al interpretar la fecha de expiración"

    # Convertir datos legibles
    iat_str = datetime.fromtimestamp(payload.get("iat")).strftime("%Y-%m-%d %H:%M:%S")
    exp_str = datetime.fromtimestamp(payload.get("exp")).strftime("%Y-%m-%d %H:%M:%S")

    return True, {
        "rfc": payload.get("rfc"),
        "creado": iat_str,
        "vence": exp_str
    }

# ----------------------------
# Exponer como módulo
# ----------------------------
__all__ = ["validate_license"]
