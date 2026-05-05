# =========================================================
#   🐧 Penguin Academy - Payments Service
# =========================================================

# Importa la funcion compartida que genera y envia logs.
from base import run_service

# Configuracion del cliente simulado de pagos.
SERVICE = {
    # Nombre que identifica al servicio en cada log.
    "name":  "payments-service",
    # Token que este cliente usa para autenticarse contra el servidor.
    "token": "svc-payments-penguin-002",
    # Plantillas de mensajes agrupadas por severidad.
    "messages": {
        # Mensajes informativos de operaciones correctas.
        "INFO":     ["Pago de ${amount} procesado para order #{id}", "Reembolso de ${amount} emitido", "Suscripción renovada para user #{id}"],
        # Mensajes de diagnostico para revisar pasos internos.
        "DEBUG":    ["Verificando fondos para order #{id}", "Conectando con gateway de pagos", "Calculando impuestos para región {region}"],
        # Mensajes de advertencia que todavia no son fallas definitivas.
        "WARN":     ["Pago rechazado para order #{id}", "Fondos insuficientes para user #{id}", "Timeout en gateway, reintentando..."],
        # Mensajes de errores del flujo de pagos.
        "ERROR":    ["Doble cobro detectado en order #{id}", "Gateway no responde: {error}", "Fallo en webhook de Stripe"],
        # Mensajes de problemas graves que afectan dinero o consistencia.
        "CRITICAL": ["FONDOS DEBITADOS SIN CONFIRMACIÓN en order #{id}", "Base de datos de pagos no responde", "Inconsistencia en balance detectada"],
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
