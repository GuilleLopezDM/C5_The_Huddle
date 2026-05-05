# =========================================================
#   🐧 Penguin Academy - Capa de base de datos
# =========================================================

# Importa SQLite para crear y consultar la base local.
import sqlite3
# Importa utilidades de fecha para generar timestamps UTC.
from datetime import datetime, timezone
# Importa la ruta de la base de datos desde la configuracion central.
from config import DB_PATH


# Devuelve la hora actual en formato ISO 8601 con zona UTC.
def now_iso() -> str:
    # Genera el timestamp con milisegundos y agrega la marca Z de UTC.
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


# Inicializa la base de datos y deja la tabla lista para usar.
def init_db():
    """Crea la tabla e índices si no existen."""
    # Abre una conexion al archivo SQLite configurado.
    conn = sqlite3.connect(DB_PATH)
    # Crea la tabla logs solo si todavia no existe.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL,
            service     TEXT    NOT NULL,
            severity    TEXT    NOT NULL,
            message     TEXT    NOT NULL
        )
    """)
    # Crea un indice para acelerar busquedas por timestamp del evento.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp   ON logs(timestamp)")
    # Crea un indice para acelerar busquedas por fecha de recepcion.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_received_at ON logs(received_at)")
    # Persiste en disco los cambios de esquema.
    conn.commit()
    # Cierra la conexion para liberar el archivo de base de datos.
    conn.close()
    # Muestra en consola que la base quedo preparada.
    print("[DB] Base de datos lista ✓")


# Inserta en la base una lista de logs ya validados.
def insert_logs(entries: list) -> int:
    """Inserta una lista de logs validados. Retorna cantidad insertada."""
    # Usa la misma fecha de recepcion para todo el batch recibido.
    received = now_iso()
    # Transforma cada log entrante al orden de columnas de la tabla.
    rows = [
        (
            # Fecha en que el servidor recibio el log.
            received,
            # Fecha original del evento enviada por el cliente.
            entry["timestamp"],
            # Nombre del servicio sin espacios sobrantes.
            entry["service"].strip(),
            # Severidad normalizada a mayusculas.
            entry["severity"].upper(),
            # Mensaje limpio de espacios al inicio y al final.
            entry["message"].strip(),
        )
        # Repite la transformacion por cada entrada valida.
        for entry in entries
    ]
    # Abre una nueva conexion para insertar los registros.
    conn = sqlite3.connect(DB_PATH)
    # Inserta todos los logs en una sola operacion batch.
    conn.executemany(
        "INSERT INTO logs (received_at, timestamp, service, severity, message) VALUES (?,?,?,?,?)",
        rows,
    )
    # Confirma la transaccion para guardar los cambios.
    conn.commit()
    # Cierra la conexion luego de insertar.
    conn.close()
    # Retorna cuantos registros se prepararon e insertaron.
    return len(rows)


# Consulta logs aplicando filtros opcionales recibidos desde la ruta GET.
def query_logs(params: dict) -> list:
    """
    Consulta logs con filtros opcionales:
      timestamp_start / timestamp_end
      received_at_start / received_at_end
    """
    # Guarda las condiciones SQL y sus valores de forma separada.
    conditions, values = [], []

    # Si llega timestamp_start, filtra eventos desde esa fecha.
    if ts := params.get("timestamp_start"):
        conditions.append("timestamp >= ?")
        values.append(ts)
    # Si llega timestamp_end, filtra eventos hasta esa fecha.
    if te := params.get("timestamp_end"):
        conditions.append("timestamp <= ?")
        values.append(te)
    # Si llega received_at_start, filtra por fecha de recepcion inicial.
    if rs := params.get("received_at_start"):
        conditions.append("received_at >= ?")
        values.append(rs)
    # Si llega received_at_end, filtra por fecha de recepcion final.
    if re_ := params.get("received_at_end"):
        conditions.append("received_at <= ?")
        values.append(re_)

    # Construye el WHERE solo cuando hay al menos una condicion.
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    # Define la consulta con orden descendente y limite de seguridad.
    sql = f"""
        SELECT id, received_at, timestamp, service, severity, message
        FROM logs {where}
        ORDER BY timestamp DESC
        LIMIT 1000
    """
    # Abre la conexion de lectura.
    conn = sqlite3.connect(DB_PATH)
    # Configura las filas para poder convertirlas facilmente a dict.
    conn.row_factory = sqlite3.Row
    # Ejecuta la consulta parametrizada para evitar inyeccion SQL.
    rows = conn.execute(sql, values).fetchall()
    # Cierra la conexion luego de leer.
    conn.close()
    # Convierte cada fila SQLite en un diccionario serializable.
    return [dict(r) for r in rows]
