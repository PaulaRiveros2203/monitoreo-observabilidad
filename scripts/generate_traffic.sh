#!/bin/bash
# Script de tráfico sintético con curl
# Uso: ./generate_traffic.sh [duracion_segundos] [req_por_segundo]

BASE_URL="http://localhost:3000"
DURATION=${1:-60}
RPS=${2:-2}
INTERVAL=$(echo "scale=3; 1/$RPS" | bc)

ENDPOINTS=(
  "/"
  "/health"
  "/api/productos"
  "/api/estadisticas"
  "/api/buscar"
  "/api/lento"
  "/api/error"
)

TOTAL=0; OK=0; ERRORS=0
START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))

echo ""
echo "🚦 Iniciando tráfico sintético (bash/curl)"
echo "   URL base : $BASE_URL"
echo "   Duración : ${DURATION}s"
echo "   Velocidad: ${RPS} req/s"
echo ""

while [ $(date +%s) -lt $END_TIME ]; do
  # Elige endpoint aleatorio
  IDX=$((RANDOM % ${#ENDPOINTS[@]}))
  ENDPOINT="${ENDPOINTS[$IDX]}"
  URL="${BASE_URL}${ENDPOINT}"

  STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL")
  TOTAL=$((TOTAL + 1))

  if [[ "$STATUS" -ge 200 && "$STATUS" -lt 400 ]]; then
    OK=$((OK + 1))
  else
    ERRORS=$((ERRORS + 1))
  fi

  ELAPSED=$(( $(date +%s) - START_TIME ))
  printf "\r⏱  %ds/%ds  |  📨 %d reqs  |  ✅ %d  |  ❌ %d" \
    "$ELAPSED" "$DURATION" "$TOTAL" "$OK" "$ERRORS"

  sleep "$INTERVAL"
done

echo ""
echo ""
echo "✅ Tráfico completado."
echo "   Total requests : $TOTAL"
echo "   Exitosos       : $OK"
echo "   Errores        : $ERRORS"
echo ""
