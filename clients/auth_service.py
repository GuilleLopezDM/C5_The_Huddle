# =========================================================
#   🐧 Penguin Academy - Auth Service
# =========================================================

# Importa la funcion compartida que genera y envia logs.
from base import run_service

# Configuracion del cliente simulado de autenticacion.
SERVICE = {
    # Nombre que identifica al servicio en cada log.
    "name":  "auth-service",
    # Token que este cliente usa para autenticarse contra el servidor.
    "token": "svc-auth-penguin-001",
    # Plantillas de mensajes agrupadas por severidad.
    "messages": {
        # Mensajes informativos de operaciones exitosas.
        "INFO":     ["Login exitoso para user #{id}", "Token renovado para user #{id}", "Sesión iniciada desde IP {ip}"],
        # Mensajes de diagnostico para seguimiento interno.
        "DEBUG":    ["Verificando JWT para user #{id}", "Cache de permisos actualizado", "Rate limit check OK para {ip}"],
        # Mensajes de advertencia sobre situaciones no criticas.
        "WARN":     ["Intento de login fallido para user #{id}", "Token próximo a expirar para user #{id}", "Demasiadas solicitudes desde {ip}"],
        # Mensajes de errores que requieren atencion.
        "ERROR":    ["JWT inválido para user #{id}", "Fallo al conectar con OAuth provider", "Error al revocar token de user #{id}"],
        # Mensajes de fallas graves del servicio.
        "CRITICAL": ["BRECHA DE SEGURIDAD detectada desde {ip}", "Servicio de autenticación caído", "Tabla de sesiones corrompida"],
    },
}


# Ejecuta este servicio con una cantidad opcional de logs.
def run(count=None) -> int:
    # Delega la generacion y envio al modulo base compartido.
    return run_service(SERVICE, count)


# Permite ejecutar este cliente directamente desde consola.
if __name__ == "__main__":
    # Lanza una ronda con cantidad aleatoria de logs.
    run()
