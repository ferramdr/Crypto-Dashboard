# Guía de Testeo con Postman

## Objetivo

Esta guía te ayudará a testear completamente la API de tu sistema distribuido de inversiones en criptomonedas usando Postman.

---

## Importar la Colección

### Paso 1: Abrir Postman

1. Abre Postman Desktop o Postman Web
2. Si no lo tienes, descárgalo de: https://www.postman.com/downloads/

### Paso 2: Importar la Colección

1. Haz clic en **"Import"** en la esquina superior izquierda
2. Selecciona el archivo: `Crypto_Investment_API.postman_collection.json`
3. Haz clic en **"Import"**

Verás la colección "Crypto Investment Tracker API" en tu panel izquierdo.

---

## Requisitos Previos

Antes de testear, asegúrate de que todo esté corriendo:

```powershell
# Verificar que Docker Compose esté corriendo
docker compose ps

# Deberías ver:
# - pg-master (PostgreSQL Master)
# - pg-replica (PostgreSQL Replica)
# - web-app (FastAPI + Streamlit)
# - pgadmin
```

**API FastAPI debe estar corriendo en:** `http://localhost:8000`

---

## Flujo de Testeo Recomendado

### Verificar Conexión

**Endpoint:** `GET /`

- **URL:** `http://localhost:8000/`
- **Descripción:** Verifica que la API esté corriendo y obtén la lista de endpoints

**Respuesta esperada:**

```json
{
  "message": "Crypto Investment Tracker API",
  "version": "1.0.0",
  "endpoints": {
    "POST /invest": "Create a new investment (writes to Master DB)",
    "GET /history": "Get investment history (reads from Replica DB)",
    "GET /stats": "Get investment statistics"
  }
}
```

---

### Health Check

**Endpoint:** `GET /health`

- **URL:** `http://localhost:8000/health`
- **Descripción:** Verifica el estado de salud de la API

**Respuesta esperada:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-25T16:00:00.000000"
}
```

---

### Crear Inversiones (WRITE → Master DB)

#### Test 1: Inversión en Bitcoin

**Endpoint:** `POST /invest`

- **URL:** `http://localhost:8000/invest`
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**

```json
{
  "coin": "bitcoin",
  "amount": 0.5
}
```

**Respuesta esperada:**

```json
{
  "status": "success",
  "message": "Investment saved to MASTER database",
  "database": "Master (172.20.0.10)",
  "investment": {
    "id": 1,
    "coin": "bitcoin",
    "amount": 0.5,
    "price_per_coin_usd": 95000.5,
    "total_value_usd": 47500.25,
    "timestamp": "2025-11-25T16:00:00"
  }
}
```

**⚠️ Nota:** El precio variará según el valor actual en CoinGecko API

---

#### Test 2: Inversión en Ethereum

**Body:**

```json
{
  "coin": "ethereum",
  "amount": 2.5
}
```

#### Test 3: Inversión en Cardano

**Body:**

```json
{
  "coin": "cardano",
  "amount": 1000
}
```

#### Test 4: Inversión en Solana

**Body:**

```json
{
  "coin": "solana",
  "amount": 10
}
```

---

### Consultar Historial (READ ← Replica DB)

**Endpoint:** `GET /history`

- **URL:** `http://localhost:8000/history`
- **Descripción:** Lee todas las inversiones desde la **REPLICA DB (172.20.0.11)**

**Respuesta esperada:**

```json
[
  {
    "id": 4,
    "coin_name": "solana",
    "amount": 10.0,
    "purchase_price_usd": 150.25,
    "timestamp": "2025-11-25T16:05:00",
    "total_value_usd": 1502.5
  },
  {
    "id": 3,
    "coin_name": "cardano",
    "amount": 1000.0,
    "purchase_price_usd": 0.45,
    "timestamp": "2025-11-25T16:04:00",
    "total_value_usd": 450.0
  },
  {
    "id": 2,
    "coin_name": "ethereum",
    "amount": 2.5,
    "purchase_price_usd": 3500.0,
    "timestamp": "2025-11-25T16:02:00",
    "total_value_usd": 8750.0
  },
  {
    "id": 1,
    "coin_name": "bitcoin",
    "amount": 0.5,
    "purchase_price_usd": 95000.5,
    "timestamp": "2025-11-25T16:00:00",
    "total_value_usd": 47500.25
  }
]
```

---

### Obtener Estadísticas (READ ← Replica DB)

**Endpoint:** `GET /stats`

- **URL:** `http://localhost:8000/stats`
- **Descripción:** Obtiene estadísticas agregadas desde la **REPLICA DB (172.20.0.11)**

**Respuesta esperada:**

```json
{
  "database": "Replica (172.20.0.11)",
  "total_investments": 4,
  "total_value_usd": 58202.75,
  "coins": {
    "bitcoin": {
      "total_amount": 0.5,
      "total_value_usd": 47500.25,
      "count": 1
    },
    "ethereum": {
      "total_amount": 2.5,
      "total_value_usd": 8750.0,
      "count": 1
    },
    "cardano": {
      "total_amount": 1000.0,
      "total_value_usd": 450.0,
      "count": 1
    },
    "solana": {
      "total_amount": 10.0,
      "total_value_usd": 1502.5,
      "count": 1
    }
  }
}
```

---

## Pruebas de Manejo de Errores

### Test 1: Moneda Inválida (Error 404)

**Endpoint:** `POST /invest`
**Body:**

```json
{
  "coin": "moneda_inexistente_123",
  "amount": 1.0
}
```

**Respuesta esperada:**

```json
{
  "detail": "Cryptocurrency 'moneda_inexistente_123' not found. Please check the coin name."
}
```

---

### Test 2: Cantidad Negativa

**Body:**

```json
{
  "coin": "bitcoin",
  "amount": -5.0
}
```

**Respuesta esperada:**

```json
{
  "detail": [
    {
      "type": "greater_than",
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

## Demostración del Patrón CQRS

### ¿Cómo demostrar Master-Slave Replication?

1. **Escribe en Master:**

   - Ejecuta `POST /invest` con una nueva inversión
   - El response indica: `"database": "Master (172.20.0.10)"`

2. **Lee desde Replica:**

   - Ejecuta `GET /history`
   - Verifica que la inversión que acabas de crear aparece en la lista
   - Esto demuestra que se **replicó automáticamente** del Master al Replica

3. **Verifica el patrón CQRS:**
   - Las **escrituras** van al Master (172.20.0.10)
   - Las **lecturas** vienen del Replica (172.20.0.11)

---

## Validación con pgAdmin

Para **validar visualmente** la replicación:

1. Abre pgAdmin: `http://localhost:5050`
2. Conéctate a **PostgreSQL Master**
3. Ejecuta una query:
   ```sql
   SELECT * FROM investments ORDER BY timestamp DESC LIMIT 5;
   ```
4. Conéctate a **PostgreSQL Replica**
5. Ejecuta la **misma query**
6. Los resultados deben ser **idénticos** → Esto demuestra la replicación

---

## Troubleshooting

### Error: "Connection refused"

- Verifica que la API esté corriendo: `docker compose ps`
- Verifica los logs: `docker compose logs web-app`

### Error: "Failed to fetch cryptocurrency price"

- Verifica tu conexión a internet
- La API de CoinGecko puede tener rate limiting

### Error: "Connection to database failed"

- Verifica que PostgreSQL Master esté corriendo
- Verifica las credenciales en `docker-compose.yml`

---

## Resumen de URLs

| Servicio                   | URL                        | Puerto |
| -------------------------- | -------------------------- | ------ |
| **FastAPI**                | http://localhost:8000      | 8000   |
| **FastAPI Docs (Swagger)** | http://localhost:8000/docs | 8000   |
| **Streamlit Dashboard**    | http://localhost:8501      | 8501   |
| **pgAdmin**                | http://localhost:5050      | 5050   |
| **PostgreSQL Master**      | localhost:5432             | 5432   |
| **PostgreSQL Replica**     | localhost:5433             | 5433   |

---

## Checklist de Demostración

- [ ] Importar colección en Postman
- [ ] Verificar conexión con `GET /`
- [ ] Crear 3-5 inversiones con `POST /invest`
- [ ] Obtener historial con `GET /history`
- [ ] Obtener estadísticas con `GET /stats`
- [ ] Probar casos de error
- [ ] Validar replicación en pgAdmin
- [ ] Mostrar dashboard de Streamlit
