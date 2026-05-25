#!/usr/bin/env python3
"""
Script de tráfico sintético para la API de monitoreo.
Genera requests automáticos a todos los endpoints.

Uso:
    python generate_traffic.py              # Por defecto: 60 segundos, 2 req/seg
    python generate_traffic.py 120 3        # 120 segundos, 3 req/seg
"""

import urllib.request
import urllib.error
import time
import random
import sys
import threading
from datetime import datetime

BASE_URL = "http://localhost:3000"

# Endpoints con peso de frecuencia (más peso = más llamadas)
ENDPOINTS = [
    ("/",               15),
    ("/health",         10),
    ("/api/productos",  30),
    ("/api/estadisticas", 20),
    ("/api/buscar",     15),
    ("/api/lento",       5),   # Menos frecuente por ser lento
    ("/api/error",       5),   # Genera errores para ver en dashboard
]

# Estadísticas locales
stats = {
    "total": 0,
    "ok": 0,
    "error": 0,
    "start_time": time.time()
}
stats_lock = threading.Lock()

def call_endpoint(url):
    """Hace una llamada HTTP y retorna (status_code, latencia_ms)."""
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            _ = resp.read()
            latency = (time.time() - start) * 1000
            return resp.status, latency
    except urllib.error.HTTPError as e:
        latency = (time.time() - start) * 1000
        return e.code, latency
    except Exception:
        latency = (time.time() - start) * 1000
        return 0, latency

def weighted_choice(endpoints):
    """Elige un endpoint con base en sus pesos."""
    total = sum(w for _, w in endpoints)
    r = random.uniform(0, total)
    cumulative = 0
    for endpoint, weight in endpoints:
        cumulative += weight
        if r <= cumulative:
            return endpoint
    return endpoints[-1][0]

def print_status(elapsed, duration):
    """Imprime el estado actual del tráfico."""
    with stats_lock:
        rps = stats["total"] / elapsed if elapsed > 0 else 0
        pct_ok = (stats["ok"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(
            f"\r⏱  {elapsed:.0f}/{duration}s  |  "
            f"📨 {stats['total']} reqs  |  "
            f"✅ {stats['ok']} ({pct_ok:.0f}%)  |  "
            f"❌ {stats['error']}  |  "
            f"🚀 {rps:.1f} req/s",
            end="", flush=True
        )

def run_traffic(duration_seconds=60, req_per_second=2):
    end_time = time.time() + duration_seconds
    interval = 1.0 / req_per_second

    print(f"\n🚦 Iniciando tráfico sintético")
    print(f"   URL base : {BASE_URL}")
    print(f"   Duración : {duration_seconds}s")
    print(f"   Velocidad: {req_per_second} req/s")
    print(f"   Endpoints: {len(ENDPOINTS)}\n")

    while time.time() < end_time:
        loop_start = time.time()
        endpoint = weighted_choice(ENDPOINTS)
        url = BASE_URL + endpoint

        status, latency = call_endpoint(url)

        with stats_lock:
            stats["total"] += 1
            if 200 <= status < 400:
                stats["ok"] += 1
            else:
                stats["error"] += 1

        elapsed = time.time() - stats["start_time"]
        remaining = end_time - time.time()
        print_status(elapsed, duration_seconds)

        # Pausa para respetar la velocidad deseada
        sleep_time = interval - (time.time() - loop_start)
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("\n\n✅ Tráfico completado.")
    with stats_lock:
        total_time = time.time() - stats["start_time"]
        print(f"   Total requests : {stats['total']}")
        print(f"   Exitosos       : {stats['ok']}")
        print(f"   Errores        : {stats['error']}")
        print(f"   Tiempo total   : {total_time:.1f}s")
        print(f"   Req/s promedio : {stats['total'] / total_time:.2f}\n")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    rps      = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    run_traffic(duration, rps)
