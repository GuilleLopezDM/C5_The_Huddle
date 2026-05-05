# =========================================================
#   🐧 Penguin Academy - POST /logs
# =========================================================

# Importa herramientas de Flask para rutas, requests y respuestas JSON.
from flask import Blueprint, request, jsonify
# Importa la funcion que guarda logs validados.
from database import insert_logs
# Importa autenticacion y validacion de cada entrada.
from validators import authenticate, validate_log_entry

# Crea el blueprint que agrupa las rutas POST de logs.
logs_post_bp = Blueprint("logs_post", __name__)


# Registra el endpoint POST /logs dentro del blueprint.
@logs_post_bp.post("/logs")
# Define la funcion que recibe uno o muchos logs.
def receive_logs():
    # Rechaza la peticion si el token no es valido.
    if not authenticate():
        return jsonify({"error": "Quién sos, bro?"}), 401

    # Intenta leer el body como JSON sin lanzar excepcion si falla.
    data = request.get_json(silent=True)
    # Si no hubo JSON valido, responde con error de cliente.
    if data is None:
        return jsonify({"error": "JSON inválido o Content-Type incorrecto"}), 400

    # Si llega un solo objeto, lo envuelve en una lista para procesarlo igual.
    if isinstance(data, dict):
        entries = [data]
    # Si llega una lista, la usa directamente como batch.
    elif isinstance(data, list):
        entries = data
    # Cualquier otro tipo de body se considera invalido.
    else:
        return jsonify({"error": "Body debe ser un objeto JSON o una lista"}), 400

    # Evita aceptar listas vacias.
    if not entries:
        return jsonify({"error": "No hay logs para guardar"}), 400

    # Prepara listas separadas para logs validos e invalidos.
    valid_entries, invalid = [], []
    # Recorre cada entrada junto con su indice original.
    for i, entry in enumerate(entries):
        # Valida formato, campos obligatorios y severity.
        ok, reason = validate_log_entry(entry)
        # Si la entrada es correcta, se guarda para insertar.
        if ok:
            valid_entries.append(entry)
        # Si la entrada falla, se registra el indice y la razon.
        else:
            invalid.append({"index": i, "reason": reason})

    # Inserta solo los logs validos; si no hay validos, guarda cero.
    saved = insert_logs(valid_entries) if valid_entries else 0

    # Construye el resumen base de la respuesta.
    response = {
        # Cantidad de logs guardados correctamente.
        "saved": saved,
        # Cantidad de logs rechazados por validacion.
        "rejected": len(invalid),
        # Cantidad total de elementos recibidos en el request.
        "total_received": len(entries),
    }
    # Agrega detalles de errores solo cuando hubo rechazos.
    if invalid:
        response["errors"] = invalid

    # Usa 207 si hubo mezcla de exitos y rechazos, 201 si todo se creo.
    status = 207 if invalid else 201
    # Devuelve el JSON final con el status HTTP calculado.
    return jsonify(response), status
