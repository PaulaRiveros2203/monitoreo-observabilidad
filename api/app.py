from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random
import threading

app = Flask(__name__)

# ── Métricas Prometheus ──────────────────────────────────────────────
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requests HTTP',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latencia de requests HTTP en segundos',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Requests activos en este momento'
)

ITEMS_IN_DB = Gauge(
    'api_items_in_database',
    'Cantidad de items en la base de datos simulada'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total de errores HTTP',
    ['endpoint', 'error_type']
)

# Datos simulados
productos = [
    {"id": 1, "nombre": "Laptop", "precio": 1200},
    {"id": 2, "nombre": "Mouse", "precio": 25},
    {"id": 3, "nombre": "Teclado", "precio": 75},
    {"id": 4, "nombre": "Monitor", "precio": 350},
    {"id": 5, "nombre": "Auriculares", "precio": 90},
]

ITEMS_IN_DB.set(len(productos))

def track_request(endpoint):
    """Decorador para rastrear métricas por endpoint."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            ACTIVE_REQUESTS.inc()
            start = time.time()
            status = 200
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                ERROR_COUNT.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start
                REQUEST_COUNT.labels(method='GET', endpoint=endpoint, status=status).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
                ACTIVE_REQUESTS.dec()
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# ── Endpoints ────────────────────────────────────────────────────────

@app.route('/')
@track_request('/')
def home():
    return jsonify({
        "servicio": "API de Monitoreo",
        "version": "1.0.0",
        "status": "activo",
        "endpoints": ["/", "/api/productos", "/api/estadisticas", "/api/lento", "/api/buscar", "/health", "/metrics"]
    })


@app.route('/health')
@track_request('/health')
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})


@app.route('/api/productos')
@track_request('/api/productos')
def get_productos():
    """Retorna lista de productos - respuesta rápida."""
    return jsonify({
        "total": len(productos),
        "productos": productos
    })


@app.route('/api/estadisticas')
@track_request('/api/estadisticas')
def get_estadisticas():
    """Retorna estadísticas calculadas - respuesta media."""
    time.sleep(random.uniform(0.1, 0.3))
    precios = [p["precio"] for p in productos]
    return jsonify({
        "total_productos": len(productos),
        "precio_promedio": sum(precios) / len(precios),
        "precio_minimo": min(precios),
        "precio_maximo": max(precios),
        "valor_inventario": sum(precios)
    })


@app.route('/api/lento')
@track_request('/api/lento')
def get_lento():
    """Simula procesamiento lento (2-3 segundos)."""
    delay = random.uniform(2.0, 3.0)
    time.sleep(delay)
    return jsonify({
        "mensaje": "Procesamiento completado",
        "tiempo_procesamiento_segundos": round(delay, 2),
        "resultado": [random.randint(1, 100) for _ in range(10)]
    })


@app.route('/api/buscar')
@track_request('/api/buscar')
def buscar():
    """Simula búsqueda con latencia variable."""
    time.sleep(random.uniform(0.05, 0.5))
    # Simula ocasionalmente un resultado vacío
    if random.random() < 0.2:
        return jsonify({"resultados": [], "total": 0})
    resultado = random.sample(productos, k=random.randint(1, len(productos)))
    return jsonify({"resultados": resultado, "total": len(resultado)})


@app.route('/api/error')
@track_request('/api/error')
def error_simulado():
    """Simula errores para ver métricas de fallo."""
    if random.random() < 0.7:
        ERROR_COUNT.labels(endpoint='/api/error', error_type='SimulatedError').inc()
        return jsonify({"error": "Error simulado intencional"}), 500
    return jsonify({"mensaje": "Esta vez funcionó"})


@app.route('/metrics')
def metrics():
    """Expone métricas en formato Prometheus."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
