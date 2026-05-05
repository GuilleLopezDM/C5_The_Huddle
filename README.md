# Penguin Academy - Servicio de Logging Distribuido

Sistema de logging distribuido hecho en Python y Flask. El proyecto simula varios servicios que generan eventos, los envian por HTTP a un servidor central, y el servidor los valida, autentica y guarda en una base SQLite para despues consultarlos con filtros.

## Que resuelve

El objetivo del challenge es tener un punto central para recibir logs de multiples servicios. Cada cliente usa un token propio, manda uno o varios logs en JSON, y el servidor responde con el resultado de la carga.

Incluye:

- Servidor Flask con endpoints `POST /logs` y `GET /logs`.
- Persistencia en SQLite.
- Autenticacion por header `Authorization`.
- Validacion de campos obligatorios y severities permitidas.
- Soporte para envio batch de logs.
- Consulta de logs con filtros por fecha del evento y fecha de recepcion.
- Tres servicios simulados con mensajes realistas.
- Modo stress test para enviar muchas rondas de logs.

## Estructura del proyecto

```text
C5_The_Huddle/
|-- README.md
|-- challenge5.md
|-- requirements.txt
|-- logging-challenge-guide.html
|-- clients/
|   |-- base.py
|   |-- run_clients.py
|   |-- auth_service.py
|   |-- payments_service.py
|   `-- socket_service.py
`-- server/
    |-- server.py
    |-- config.py
    |-- database.py
    |-- validators.py
    |-- logs.db
    `-- routes/
        |-- logs_post.py
        |-- logs_get.py
        `-- __init__.py
```

## Requisitos

- Python 3.10 o superior.
- Flask.

Instalacion:

```bash
pip install -r requirements.txt
```

## Como ejecutar

Usa dos terminales: una para el servidor y otra para los clientes.

### 1. Levantar el servidor

```bash
cd server
python server.py
```

El servidor queda disponible en:

```text
http://localhost:8080
```

### 2. Ejecutar los clientes simulados

En otra terminal:

```bash
cd clients
python run_clients.py
```

Esto ejecuta una ronda de logs para:

- `auth-service`
- `payments-service`
- `socket-service`

Tambien prueba un token invalido para demostrar la respuesta `401`.

### 3. Ejecutar stress test

```bash
cd clients
python run_clients.py --stress 50
```

El numero indica cuantas rondas se ejecutan. En cada ronda se generan logs para todos los servicios.

## API

### POST `/logs`

Recibe un log individual o una lista de logs.

Header requerido:

```http
Authorization: Token svc-auth-penguin-001
Content-Type: application/json
```

Body con un solo log:

```json
{
  "timestamp": "2026-05-03T12:00:00.000Z",
  "service": "auth-service",
  "severity": "ERROR",
  "message": "JWT invalido para user #1234"
}
```

Body con varios logs:

```json
[
  {
    "timestamp": "2026-05-03T12:00:00.000Z",
    "service": "auth-service",
    "severity": "INFO",
    "message": "Login exitoso para user #1234"
  },
  {
    "timestamp": "2026-05-03T12:01:00.000Z",
    "service": "payments-service",
    "severity": "WARN",
    "message": "Timeout en gateway, reintentando..."
  }
]
```

Respuesta exitosa:

```json
{
  "saved": 2,
  "rejected": 0,
  "total_received": 2
}
```

Si hay logs validos e invalidos mezclados, el servidor responde `207 Multi-Status` e incluye los errores por indice:

```json
{
  "saved": 1,
  "rejected": 1,
  "total_received": 2,
  "errors": [
    {
      "index": 1,
      "reason": "Campo faltante: 'message'"
    }
  ]
}
```

### GET `/logs`

Devuelve logs guardados en la base de datos. Requiere un token valido.

Filtros opcionales:

| Parametro | Descripcion |
| --- | --- |
| `timestamp_start` | Fecha minima del evento |
| `timestamp_end` | Fecha maxima del evento |
| `received_at_start` | Fecha minima de recepcion en el servidor |
| `received_at_end` | Fecha maxima de recepcion en el servidor |

Ejemplo:

```bash
curl -H "Authorization: Token svc-auth-penguin-001" "http://localhost:8080/logs?timestamp_start=2026-05-03T00:00:00Z&timestamp_end=2026-05-03T23:59:59Z"
```

Respuesta:

```json
{
  "count": 1,
  "filters_applied": {
    "timestamp_start": "2026-05-03T00:00:00Z",
    "timestamp_end": "2026-05-03T23:59:59Z"
  },
  "logs": [
    {
      "id": 1,
      "received_at": "2026-05-03T12:02:15.120Z",
      "timestamp": "2026-05-03T12:00:00.000Z",
      "service": "auth-service",
      "severity": "ERROR",
      "message": "JWT invalido para user #1234"
    }
  ]
}
```

## Tokens validos

Los tokens estan definidos en `server/config.py`.

| Servicio | Token |
| --- | --- |
| `auth-service` | `svc-auth-penguin-001` |
| `payments-service` | `svc-payments-penguin-002` |
| `socket-service` | `svc-socket-penguin-004` |

El header debe incluir la palabra `Token` antes del valor:

```http
Authorization: Token svc-auth-penguin-001
```

Si el token no existe o no se envia, el servidor responde:

```json
{
  "error": "Quien sos, bro?"
}
```

## Formato de log

Cada log debe tener estos campos:

| Campo | Tipo | Detalle |
| --- | --- | --- |
| `timestamp` | string | Fecha/hora del evento en formato ISO 8601 |
| `service` | string | Nombre del servicio que genero el log |
| `severity` | string | Nivel del evento |
| `message` | string | Descripcion del evento |

Severities aceptadas:

```text
INFO, DEBUG, WARN, WARNING, ERROR, CRITICAL
```

## Base de datos

La base usa SQLite y se inicializa automaticamente al levantar el servidor. La tabla principal es `logs`, con estos campos:

- `id`
- `received_at`
- `timestamp`
- `service`
- `severity`
- `message`

Tambien se crean indices sobre `timestamp` y `received_at` para mejorar las consultas con filtros.

## Ejemplo rapido con curl

Con el servidor levantado:

```bash
curl -X POST "http://localhost:8080/logs" \
  -H "Authorization: Token svc-auth-penguin-001" \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\":\"2026-05-03T12:00:00.000Z\",\"service\":\"auth-service\",\"severity\":\"INFO\",\"message\":\"Login exitoso\"}"
```

Consultar:

```bash
curl -H "Authorization: Token svc-auth-penguin-001" "http://localhost:8080/logs"
```

## Checklist del challenge

- [x] Multiples servicios simulados generando logs.
- [x] Envio de logs en JSON usando `POST /logs`.
- [x] Soporte para enviar un log o una lista de logs.
- [x] Logs guardados en SQLite.
- [x] Endpoint `GET /logs` con filtros funcionales.
- [x] Tokens unicos por servicio.
- [x] Respuestas HTTP claras para errores de autenticacion y validacion.
- [x] Stress test desde `clients/run_clients.py`.
