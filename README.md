# 📊 API Monitoreo y Observabilidad

Sistema completo de monitoreo usando **Prometheus** y **Grafana** para una API REST construida en Python/Flask.

---

## 👤 Información del Estudiante

- **Nombre:** [Tu nombre completo aquí]
- **Código:** [Tu código de estudiante aquí]
- **Repositorio:** [URL del repositorio]
- **Video:** [URL del video demostrativo]

---

## 🏗️ Arquitectura

```
┌─────────────┐     scraping      ┌──────────────┐     datasource    ┌─────────────┐
│   API REST  │ ◄──── /metrics ── │  Prometheus  │ ◄──────────────── │   Grafana   │
│  Flask      │                   │  :9090       │                   │  :3001      │
│  :3000      │                   └──────────────┘                   └─────────────┘
└─────────────┘
       ▲
       │  requests
┌─────────────┐
│   Script    │
│  de tráfico │
└─────────────┘
```

---

## 📁 Estructura del Proyecto

```
monitoring-project/
├── docker-compose.yml              # Orquestación de servicios
├── README.md                       # Este archivo
│
├── api/
│   ├── Dockerfile                  # Imagen de la API
│   ├── requirements.txt            # Dependencias Python
│   └── app.py                      # API Flask con métricas
│
├── prometheus/
│   └── prometheus.yml              # Configuración de scraping
│
├── grafana/
│   ├── dashboards/
│   │   └── api-dashboard.json      # Dashboard pre-configurado (7 paneles)
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml      # Auto-conexión a Prometheus
│       └── dashboards/
│           └── dashboard.yml       # Auto-carga del dashboard
│
└── scripts/
    ├── generate_traffic.py         # Generador de tráfico (Python)
    └── generate_traffic.sh         # Generador de tráfico (Bash)
```

---

## 🚀 Cómo ejecutar

### Prerequisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo

### Paso 1 – Levantar todos los servicios

```bash
docker-compose up -d
```

Espera ~30 segundos a que todo inicialice.

### Paso 2 – Verificar que los servicios corren

```bash
docker-compose ps
```

Deberías ver los 3 servicios en estado `Up`.

### Paso 3 – Acceder a los servicios

| Servicio   | URL                        | Usuario/Contraseña |
|------------|----------------------------|--------------------|
| API        | http://localhost:3000      | —                  |
| Prometheus | http://localhost:9090      | —                  |
| Grafana    | http://localhost:3001      | admin / admin      |

---

## 🔌 Endpoints de la API

| Método | Endpoint            | Descripción                          | Latencia aprox. |
|--------|---------------------|--------------------------------------|-----------------|
| GET    | `/`                 | Info general del servicio            | ~10ms           |
| GET    | `/health`           | Health check                         | ~5ms            |
| GET    | `/api/productos`    | Lista de productos                   | ~10ms           |
| GET    | `/api/estadisticas` | Estadísticas calculadas              | ~100-300ms      |
| GET    | `/api/buscar`       | Búsqueda con latencia variable       | ~50-500ms       |
| GET    | `/api/lento`        | Procesamiento lento (2-3 segundos)   | ~2000-3000ms    |
| GET    | `/api/error`        | Simula errores (70% falla)           | variable        |
| GET    | `/metrics`          | Métricas en formato Prometheus       | ~5ms            |

---

## 📈 Métricas expuestas

| Métrica                                    | Tipo      | Descripción                              |
|--------------------------------------------|-----------|------------------------------------------|
| `http_requests_total`                      | Counter   | Total de requests por endpoint y status  |
| `http_request_duration_seconds`            | Histogram | Latencia de cada request                 |
| `http_active_requests`                     | Gauge     | Requests activos en este momento         |
| `http_errors_total`                        | Counter   | Total de errores por tipo                |
| `api_items_in_database`                    | Gauge     | Items en la base de datos simulada       |

---

## 🔍 Queries PromQL útiles

```promql
# Requests por segundo (último minuto)
sum by (endpoint) (rate(http_requests_total[1m]))

# Latencia promedio en ms
rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m]) * 1000

# Percentil 95 de latencia
histogram_quantile(0.95, sum by (le, endpoint) (rate(http_request_duration_seconds_bucket[5m])))

# Tasa de errores
sum(rate(http_errors_total[1m]))

# Requests activos ahora
http_active_requests
```

---

## 🚦 Generar tráfico sintético

### Opción A – Python (recomendado)

```bash
# 60 segundos, 2 requests por segundo (por defecto)
python scripts/generate_traffic.py

# 120 segundos, 5 requests por segundo
python scripts/generate_traffic.py 120 5
```

### Opción B – Bash (requiere curl)

```bash
chmod +x scripts/generate_traffic.sh
./scripts/generate_traffic.sh 60 2
```

---

## 📊 Dashboard de Grafana

El dashboard **"API Monitoreo - Dashboard Principal"** se carga automáticamente con 7 paneles:

1. **Throughput** – Requests por segundo por endpoint
2. **Latencia Promedio** – En milisegundos por endpoint
3. **Requests Activos** – Gauge en tiempo real
4. **Total Requests** – Acumulado desde el inicio
5. **Tasa de Errores** – Errores por segundo
6. **Percentil 95** – Latencia p95 por endpoint
7. **Requests por Endpoint** – Barras con los últimos 5 minutos

---

## 🛑 Detener el proyecto

```bash
# Detener servicios (conserva datos)
docker-compose down

# Detener y eliminar todos los datos
docker-compose down -v
```

---

## 🔄 Reinicio limpio (antes de grabar el video)

```bash
docker-compose down -v
docker-compose up -d
docker-compose ps
```

---

## 🛠️ Tecnologías usadas

- **Python 3.11** + **Flask 3.0** – API REST
- **prometheus-client** – Instrumentación de métricas
- **Prometheus** – Recolección y almacenamiento de métricas
- **Grafana** – Visualización y dashboards
- **Docker** + **Docker Compose** – Orquestación de contenedores
