# =========================================================
#   🐧 Penguin Academy - Validación de logs
# =========================================================

# Importa expresiones regulares para validar el formato del timestamp.
import re
# Importa el objeto request para leer headers y parametros de Flask.
from flask import request
# Importa los tokens validos definidos en la configuracion central.
from config import VALID_TOKENS

# Conjunto de severities permitidos para cada log recibido.
VALID_SEVERITIES = {"INFO", "DEBUG", "WARN", "WARNING", "ERROR", "CRITICAL"}


# Define una funcion que valida si la peticion esta autenticada.
def authenticate() -> bool:
    """Verifica el token en el header Authorization."""
    # Compara el header Authorization con las claves aceptadas en VALID_TOKENS.
    return request.headers.get("Authorization", "") in VALID_TOKENS


# Define una funcion que valida un log individual.
def validate_log_entry(entry: dict) -> tuple[bool, str | None]:
    """
    Valida que un log tenga los campos requeridos y formato correcto.
    Retorna (True, None) si válido, (False, motivo) si no.
    """
    # Recorre los campos obligatorios que debe traer cada log.
    for field in ["timestamp", "service", "severity", "message"]:
        # Si falta un campo, devuelve False junto con el motivo.
        if field not in entry:
            return False, f"Campo faltante: '{field}'"

    # Normaliza severity a mayusculas y verifica que este permitido.
    if entry["severity"].upper() not in VALID_SEVERITIES:
        return False, f"Severity inválido: '{entry['severity']}'. Válidos: {VALID_SEVERITIES}"

    # Valida que el timestamp empiece con una forma ISO 8601 basica.
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", entry["timestamp"]):
        return False, "Timestamp debe ser ISO 8601 (ej: 2025-01-01T12:00:00Z)"

    # Evita guardar mensajes vacios o formados solo por espacios.
    if not entry["message"].strip():
        return False, "Message no puede estar vacío"

    # Si pasa todas las validaciones, el log es valido.
    return True, None
