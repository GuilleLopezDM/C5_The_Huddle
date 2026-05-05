# =========================================================
#   🐧 Penguin Academy - Configuración central
# =========================================================

# Ruta del archivo SQLite donde se guardan los logs.
DB_PATH = "logs.db"

# Diccionario de tokens aceptados por la API.
VALID_TOKENS = {
    # Token valido para el cliente de autenticacion.
    "Token svc-auth-penguin-001":     "auth-service",
    # Token valido para el cliente de pagos.
    "Token svc-payments-penguin-002": "payments-service",
    # Token valido para el cliente de sockets.
    "Token svc-socket-penguin-004":   "socket-service",
}
