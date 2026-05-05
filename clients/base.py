# =========================================================
#   🐧 Penguin Academy - Base compartida de clientes
# =========================================================
#   Lógica común: generación de logs, envío HTTP,
#   placeholders aleatorios y distribución de severities.
# =========================================================

# Importa JSON para serializar los logs antes de enviarlos.
import json
# Importa random para elegir mensajes, severities y datos ficticios.
import random
# Importa urllib.request para hacer el POST HTTP sin dependencias externas.
import urllib.request
# Importa urllib.error para manejar errores HTTP y de conexion.
import urllib.error
# Importa utilidades de fecha para crear timestamps recientes.
from datetime import datetime, timezone, timedelta

# URL del endpoint central que recibe los logs.
SERVER_URL = "http://localhost:8080/logs"

# Distribucion ponderada para que INFO/DEBUG aparezcan mas que CRITICAL.
SEVERITY_WEIGHTS = {
    # Peso de logs informativos.
    "INFO":     40,
    # Peso de logs de diagnostico.
    "DEBUG":    25,
    # Peso de logs de advertencia.
    "WARN":     20,
    # Peso de logs de error.
    "ERROR":    12,
    # Peso de logs criticos.
    "CRITICAL":  3,
}


# Genera valores aleatorios que rellenan las plantillas de mensajes.
def random_placeholder() -> dict:
    """Genera valores aleatorios para rellenar templates de mensajes."""
    # Devuelve un diccionario con todos los placeholders posibles.
    return {
        # Identificador numerico para usuarios, ordenes o clientes.
        "id":      random.randint(1000, 99999),
        # Direccion IP ficticia.
        "ip":      f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        # Monto aleatorio para logs de pagos.
        "amount":  round(random.uniform(1.5, 9999.99), 2),
        # Region aleatoria para mensajes regionales.
        "region":  random.choice(["AR", "BR", "MX", "US", "EU", "UY", "PY"]),
        # Codigo de error ficticio.
        "error":   random.choice(["CONNECTION_REFUSED", "TIMEOUT", "SSL_ERROR", "DNS_FAIL"]),
        # Puntaje aleatorio para posibles mensajes de scoring.
        "score":   round(random.uniform(-10, 100), 2),
        # Conteo aleatorio para cantidades agregadas.
        "count":   random.randint(1, 5000),
        # Nombre de comunidad ficticia.
        "sub":     random.choice(["r/memes", "r/dankmemes", "r/programmerhumor", "r/technicallythetruth"]),
        # Numero de sala para mensajes de sockets.
        "room":    random.randint(1, 999),
        # Minutos de inactividad o espera.
        "mins":    random.randint(5, 120),
        # Numero de intento para reintentos.
        "attempt": random.randint(1, 10),
        # Metodo HTTP ficticio.
        "method":  random.choice(["GET", "POST", "PUT", "DELETE", "PATCH"]),
        # Ruta HTTP ficticia.
        "path":    random.choice(["/api/users", "/api/memes", "/api/payments", "/ws/connect", "/health"]),
        # Duracion aleatoria en milisegundos.
        "ms":      random.randint(50, 30000),
        # Servicio aleatorio para mensajes cruzados.
        "service": random.choice(["auth-service", "payments-service", "socket-service"]),
        # Dominio aleatorio para mensajes de red.
        "domain":  random.choice(["penguin.academy", "api.penguin.io", "ws.penguin.io"]),
    }


# Genera un log individual para el servicio indicado.
def generate_log(service: dict) -> dict:
    """Genera un log realista para el servicio dado."""
    # Obtiene los nombres de severidad disponibles.
    severities = list(SEVERITY_WEIGHTS.keys())
    # Obtiene los pesos asociados a cada severidad.
    weights    = list(SEVERITY_WEIGHTS.values())
    # Elige una severidad respetando la distribucion ponderada.
    severity   = random.choices(severities, weights=weights, k=1)[0]

    # Elige una plantilla compatible con la severidad elegida.
    template   = random.choice(service["messages"][severity])
    # Rellena los placeholders de la plantilla con valores aleatorios.
    message    = template.format(**random_placeholder())

    # Define cuantos minutos hacia atras ocurrio el evento.
    minutes_ago = random.randint(0, 60)
    # Calcula la fecha del evento en UTC.
    event_time  = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    # Formatea el timestamp con milisegundos y sufijo Z.
    timestamp   = event_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Devuelve el log con el formato que espera el servidor.
    return {
        # Fecha original del evento.
        "timestamp": timestamp,
        # Nombre del servicio emisor.
        "service":   service["name"],
        # Severidad seleccionada.
        "severity":  severity,
        # Mensaje final ya formateado.
        "message":   message,
    }


# Envia un batch de logs al servidor central.
def send_logs(service: dict, logs: list) -> dict:
    """
    Envía una lista de logs al servidor central.
    Retorna el resultado del servidor o info del error.
    """
    # Define los headers necesarios para JSON y autenticacion.
    headers = {
        # Indica que el body esta serializado como JSON.
        "Content-Type":  "application/json",
        # Construye el header Authorization con el token del servicio.
        "Authorization": f"Token {service['token']}",
    }
    # Convierte la lista de logs a bytes JSON para enviarla por HTTP.
    body = json.dumps(logs).encode()

    # Intenta enviar la peticion y parsear la respuesta.
    try:
        # Construye el request POST hacia el servidor.
        req = urllib.request.Request(SERVER_URL, data=body, headers=headers, method="POST")
        # Ejecuta el request con timeout para evitar esperas infinitas.
        with urllib.request.urlopen(req, timeout=10) as resp:
            # Devuelve status HTTP y body JSON cuando la respuesta es exitosa.
            return {"status": resp.status, "body": json.loads(resp.read())}
    # Captura respuestas HTTP con codigo de error como 400 o 401.
    except urllib.error.HTTPError as e:
        # Lee el cuerpo de error enviado por el servidor.
        body_err = e.read().decode()
        # Devuelve codigo HTTP y cuerpo parseado si existe.
        return {"status": e.code, "body": json.loads(body_err) if body_err else {}}
    # Captura errores de conexion, por ejemplo servidor apagado.
    except urllib.error.URLError as e:
        # Normaliza el error para que el caller pueda imprimirlo.
        return {"status": 0, "body": {"error": f"No se pudo conectar: {e.reason}"}}


# Genera y envia logs para un servicio concreto.
def run_service(service: dict, count: int | None = None) -> int:
    """
    Genera y envía un batch de logs para un servicio.
    Imprime el resultado y retorna la cantidad guardada.
    """
    # Si no se pasa cantidad, elige un batch pequeno aleatorio.
    if count is None:
        count = random.randint(3, 8)

    # Genera la lista de logs para enviar.
    logs   = [generate_log(service) for _ in range(count)]
    # Envia la lista al servidor central.
    result = send_logs(service, logs)
    # Extrae el status HTTP devuelto.
    status = result["status"]
    # Extrae el body devuelto.
    body   = result["body"]

    # Informa en consola que se esta enviando un batch.
    print(f"\n[{service['name']}] Enviando {count} logs...")

    # Trata 201 y 207 como respuestas utiles del servidor.
    if status in (201, 207):
        # Lee cuantos logs fueron guardados.
        saved    = body.get("saved", 0)
        # Lee cuantos logs fueron rechazados.
        rejected = body.get("rejected", 0)
        # Imprime el resumen del resultado.
        print(f"    ✓ Guardados: {saved} | Rechazados: {rejected}")
        # Define iconos por severidad para imprimir una muestra legible.
        icons = {"INFO": "ℹ", "DEBUG": "🐛", "WARN": "⚠", "ERROR": "✗", "CRITICAL": "💀"}
        # Muestra como ejemplo los primeros tres logs generados.
        for log in logs[:3]:
            # Obtiene el icono asociado a la severidad del log.
            icon = icons.get(log["severity"], "?")
            # Imprime severity y los primeros caracteres del mensaje.
            print(f"    {icon} [{log['severity']:8}] {log['message'][:60]}")
        # Si habia mas de tres logs, resume el resto.
        if len(logs) > 3:
            print(f"    ... y {len(logs)-3} más")
        # Retorna cuantos logs guardo realmente el servidor.
        return saved
    # Si el status no fue exitoso, imprime el error recibido.
    else:
        print(f"    ✗ Error {status}: {body}")
        # Retorna cero porque no se confirmo ningun guardado.
        return 0
