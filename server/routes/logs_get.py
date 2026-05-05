# =========================================================
#   🐧 Penguin Academy - GET /logs
# =========================================================

# Importa herramientas Flask para definir rutas y responder JSON.
from flask import Blueprint, request, jsonify
# Importa la funcion que consulta logs en la base.
from database import query_logs
# Importa la validacion del token Authorization.
from validators import authenticate

# Crea el blueprint que agrupa las rutas GET de logs.
logs_get_bp = Blueprint("logs_get", __name__)


# Registra el endpoint GET /logs dentro del blueprint.
@logs_get_bp.get("/logs")
# Define la funcion que devuelve los logs consultados.
def get_logs():
    # Rechaza la peticion si el token no esta autorizado.
    if not authenticate():
        return jsonify({"error": "Quién sos, bro?"}), 401

    # Convierte los query params de Flask a un diccionario simple.
    params = {k: v for k, v in request.args.items()}
    # Consulta la base aplicando los filtros recibidos.
    logs = query_logs(params)

    # Devuelve cantidad, filtros usados y la lista de logs.
    return jsonify({
        # Cantidad de registros encontrados.
        "count": len(logs),
        # Filtros recibidos en la URL.
        "filters_applied": params,
        # Registros devueltos por la consulta.
        "logs": logs,
    }), 200
