# =========================================================
#   🐧 Penguin Academy - Entry point del servidor
# =========================================================

# Importa Flask para crear la aplicacion web.
from flask import Flask
# Importa la inicializacion de la base de datos.
from database import init_db
# Importa los blueprints que exponen POST /logs y GET /logs.
from routes import logs_post_bp, logs_get_bp

# Crea la instancia principal de Flask.
app = Flask(__name__)
# Registra la ruta encargada de recibir logs.
app.register_blueprint(logs_post_bp)
# Registra la ruta encargada de consultar logs.
app.register_blueprint(logs_get_bp)

# Ejecuta este bloque solo cuando el archivo se corre directamente.
if __name__ == "__main__":
    # Prepara la base de datos antes de aceptar requests.
    init_db()
    # Imprime un separador visual en consola.
    print("=" * 55)
    # Muestra el nombre del servidor.
    print("  🐧 Penguin Academy - Log Server (Flask)")
    # Muestra la URL local donde queda escuchando Flask.
    print("  📡 http://localhost:8080")
    # Muestra el endpoint para enviar logs.
    print("  POST /logs  → Enviar logs")
    # Muestra el endpoint para consultar logs.
    print("  GET  /logs  → Consultar logs")
    # Cierra el bloque visual de informacion.
    print("=" * 55)
    # Arranca el servidor en todas las interfaces, puerto 8080.
    app.run(host="0.0.0.0", port=8080, debug=False)
