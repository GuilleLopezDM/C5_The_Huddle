# =========================================================
#   🐧 Penguin Academy - Socket Service
# =========================================================

# Importa la funcion compartida que genera y envia logs.
from base import run_service

# Configuracion del cliente simulado de sockets.
SERVICE = {
    # Nombre que identifica al servicio en cada log.
    "name":  "socket-service",
    # Token que este cliente usa para autenticarse contra el servidor.
    "token": "svc-socket-penguin-004",
    # Plantillas de mensajes agrupadas por severidad.
    "messages": {
        # Mensajes informativos sobre conexiones y actividad normal.
        "INFO":     ["Cliente {id} conectado via WebSocket", "{count} clientes activos en sala #{room}", "Mensaje broadcast enviado a {count} clientes"],
        # Mensajes de diagnostico de bajo nivel del socket.
        "DEBUG":    ["Ping/Pong con cliente {id}", "Reconectando cliente {id}...", "Handshake completado con {id}"],
        # Mensajes de advertencia por condiciones recuperables.
        "WARN":     ["Cliente {id} sin actividad por {mins} min", "Buffer lleno para cliente {id}", "Reconexión #{attempt} para cliente {id}"],
        # Mensajes de error en conexiones o broadcasts.
        "ERROR":    ["Conexión cerrada inesperadamente: cliente {id}", "Fallo en broadcast a sala #{room}", "Timeout en socket {id}"],
        # Mensajes de fallas graves del servicio de sockets.
        "CRITICAL": ["TODOS LOS WEBSOCKETS CAÍDOS", "Memory leak en sala #{room}", "El socket service colapsó (otra vez)"],
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
