"""
=========================================================
  🐧 Penguin Academy - Orquestador de clientes
=========================================================
  Ejecuta todos los servicios simulados en orden.

  Uso:
    python run_clients.py              → una ronda
    python run_clients.py --stress 50  → 50 rondas
=========================================================
"""

# Importa sys para leer argumentos de linea de comandos.
import sys
# Importa time para medir duracion del stress test.
import time
# Importa random para elegir cantidades variables por ronda.
import random

# Importa el cliente simulado de autenticacion.
import auth_service
# Importa el cliente simulado de pagos.
import payments_service
# Importa el cliente simulado de sockets.
import socket_service
# Importa utilidades compartidas para generar y enviar logs.
from base import generate_log, send_logs

# Lista de modulos de servicios que se ejecutaran en cada ronda.
SERVICES_MODULES = [
    # Servicio de autenticacion.
    auth_service,
    # Servicio de pagos.
    payments_service,
    # Servicio de sockets.
    socket_service,
]


# Ejecuta una prueba controlada con un token invalido.
def send_invalid_token_example():
    """Demuestra el rechazo de tokens inválidos."""
    # Informa en consola que se probara autenticacion fallida.
    print("\n[🔐] Probando token inválido...")
    # Define un servicio ficticio con token no autorizado.
    fake = {"name": "hacker-service", "token": "svc-fake-token-lol"}
    # Generamos un log con la estructura de auth_service para tener mensajes válidos
    # Crea un log valido en contenido, pero asociado al servicio falso.
    log = generate_log({**auth_service.SERVICE, **fake})
    # Envia ese log para comprobar que el servidor rechaza el token.
    result = send_logs(fake, [log])
    # Imprime el codigo HTTP y el body devuelto por el servidor.
    print(f"    → Status: {result['status']} | Respuesta: {result['body']}")


# Ejecuta muchas rondas de envio para probar volumen.
def stress_test(rounds: int):
    """Envía múltiples rondas de logs para probar performance."""
    # Imprime el tamano del stress test antes de empezar.
    print(f"\n[🔥] STRESS TEST - {rounds} rondas x {len(SERVICES_MODULES)} servicios")
    # Acumula cuantos logs confirmo el servidor.
    total_sent = 0
    # Guarda el tiempo inicial para medir duracion total.
    start = time.time()

    # Repite el envio tantas rondas como pida el usuario.
    for i in range(rounds):
        # Ejecuta cada servicio simulado dentro de la ronda actual.
        for mod in SERVICES_MODULES:
            # Elige una cantidad aleatoria de logs para este servicio.
            count  = random.randint(5, 20)
            # Ejecuta el servicio y recibe cuantos logs guardo.
            saved  = mod.run(count)
            # Suma los guardados al acumulador general.
            total_sent += saved

        # Cada 10 rondas imprime un avance.
        if (i + 1) % 10 == 0:
            # Calcula cuantos segundos pasaron desde el inicio.
            elapsed = time.time() - start
            # Muestra ronda actual, total guardado y tiempo parcial.
            print(f"    Ronda {i+1}/{rounds} | Total guardados: {total_sent} | Tiempo: {elapsed:.1f}s")

    # Calcula el tiempo final al terminar todas las rondas.
    elapsed = time.time() - start
    # Imprime resumen final con throughput aproximado.
    print(f"\n[✓] Stress test completado: {total_sent} logs en {elapsed:.2f}s ({total_sent/elapsed:.0f} logs/seg)")


# Punto principal del orquestador.
def main():
    # Detecta si el usuario paso el flag --stress.
    stress = "--stress" in sys.argv
    # Si hay stress, lee la cantidad posterior al flag; si no, usa una ronda.
    rounds = int(sys.argv[sys.argv.index("--stress") + 1]) if stress else 1

    # Si se pidio stress test, ejecuta ese modo y termina.
    if stress:
        stress_test(rounds)
        return

    # Imprime una cabecera visual para la ejecucion normal.
    print("=" * 55)
    # Muestra el titulo del orquestador.
    print("  🐧 Penguin Academy - Servicios Simulados")
    # Cierra la cabecera visual.
    print("=" * 55)

    # Ejecuta todos los servicios una vez y suma los logs guardados.
    total_saved = sum(mod.run() for mod in SERVICES_MODULES)

    # Ejecuta una prueba negativa para validar rechazo de token.
    send_invalid_token_example()

    # Imprime separador final.
    print(f"\n{'='*55}")
    # Imprime el total guardado durante la ronda normal.
    print(f"  Total logs guardados: {total_saved}")
    # Muestra el endpoint para consultar los logs.
    print(f"  Consultá los logs en: GET http://localhost:8080/logs")
    # Cierra el bloque final.
    print(f"{'='*55}")


# Ejecuta main solo cuando este archivo se corre directamente.
if __name__ == "__main__":
    # Lanza el flujo principal.
    main()
