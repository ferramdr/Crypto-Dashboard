# 🚀 Backend Python FastAPI - Documentación Completa

## 📁 Estructura de Archivos Creados

```
web/
├── requirements.txt    # Dependencias de Python
├── database.py        # Configuración CQRS (Master/Replica)
├── models.py          # Modelo SQLAlchemy (Investment)
└── main.py            # Aplicación FastAPI con endpoints
```

## 🎯 Patrón CQRS Implementado

### **Command (Escritura) → Master DB**

- **IP**: `172.20.0.10:5432`
- **Operaciones**: INSERT, UPDATE, DELETE
- **Endpoint**: `POST /invest`

### **Query (Lectura) → Replica DB**

- **IP**: `172.20.0.11:5432`
- **Operaciones**: SELECT
- **Endpoints**: `GET /history`, `GET /stats`

## 🌐 API Endpoints Disponibles

### 1️⃣ **Root Endpoint**

```bash
GET http://localhost:8000/
```

**Response:**

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

### 2️⃣ **Crear Inversión** (WRITE → Master)

```bash
POST http://localhost:8000/invest
Content-Type: application/json

{
  "coin": "bitcoin",
  "amount": 0.5
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Investment saved to MASTER database",
  "database": "Master (172.20.0.10)",
  "investment": {
    "id": 1,
    "coin": "bitcoin",
    "amount": 0.5,
    "price_per_coin_usd": 88461.01,
    "total_value_usd": 44230.505,
    "timestamp": "2025-11-24T20:04:13.300727"
  }
}
```

> [!NOTE]
> Este endpoint consulta la **API de CoinGecko** en tiempo real para obtener el precio actual de la criptomoneda.

### 3️⃣ **Ver Historial** (READ → Replica)

```bash
GET http://localhost:8000/history
```

**Response Example:**

```json
[
  {
    "id": 1,
    "coin_name": "bitcoin",
    "amount": 0.5,
    "purchase_price_usd": 88461.01,
    "timestamp": "2025-11-24T20:04:13.300727",
    "total_value_usd": 44230.5
  }
]
```

### 4️⃣ **Estadísticas** (READ → Replica)

```bash
GET http://localhost:8000/stats
```

**Response Example:**

```json
{
  "database": "Replica (172.20.0.11)",
  "total_investments": 1,
  "total_value_usd": 44230.5,
  "coins": {
    "bitcoin": {
      "total_amount": 0.5,
      "total_value_usd": 44230.5,
      "count": 1
    }
  }
}
```

### 5️⃣ **Health Check**

```bash
GET http://localhost:8000/health
```

## 🔧 Comandos Útiles

### Iniciar el servidor (ya está corriendo):

```bash
docker exec -d web-app uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Ver logs del servidor:

```bash
docker logs -f web-app
```

### Acceder al contenedor:

```bash
docker exec -it web-app bash
```

### Reinstalar dependencias:

```bash
docker exec web-app pip install -r requirements.txt
```

## 📊 Pruebas de Verificación CQRS

### PowerShell - Crear Inversión:

```powershell
curl.exe -X POST 'http://localhost:8000/invest' -H 'Content-Type: application/json' -d '{\"coin\":\"bitcoin\",\"amount\":0.5}'
```

### PowerShell - Ver Historial:

```powershell
curl.exe http://localhost:8000/history
```

### PowerShell - Ver Estadísticas:

```powershell
curl.exe http://localhost:8000/stats
```

### Bash/Linux - Crear Inversión:

```bash
curl -X POST 'http://localhost:8000/invest' \
  -H 'Content-Type: application/json' \
  -d '{"coin":"ethereum","amount":2.0}'
```

## 🌍 Integración con CoinGecko API

El endpoint `/invest` consulta automáticamente la API pública de CoinGecko:

**URL consultada:**

```
https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd
```

**Criptomonedas soportadas** (ejemplos):

- `bitcoin`
- `ethereum`
- `cardano`
- `solana`
- `ripple`
- `dogecoin`
- `polkadot`

> [!TIP]
> Para ver la lista completa de criptomonedas soportadas, visita: https://api.coingecko.com/api/v3/coins/list

## 📚 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

### Swagger UI:

```
http://localhost:8000/docs
```

### ReDoc:

```
http://localhost:8000/redoc
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐
│   Cliente Web   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI App   │
│   (Port 8000)   │
│  172.20.0.20    │
└────┬───────┬────┘
     │       │
WRITE│       │READ
     │       │
     ▼       ▼
┌─────────┐ ┌─────────┐
│ Master  │ │ Replica │
│ DB      │→│ DB      │
│172.20   │ │172.20   │
│.0.10    │ │.0.11    │
└─────────┘ └─────────┘
```

## ✅ Verificación de Funcionamiento

### 1. Verificar que el contenedor esté corriendo:

```bash
docker ps | findstr web-app
```

### 2. Verificar conectividad a las bases de datos:

```bash
# Master DB
docker exec web-app python -c "from database import engine_master; print(engine_master.url)"

# Replica DB
docker exec web-app python -c "from database import engine_replica; print(engine_replica.url)"
```

### 3. Verificar tabla creada en Master:

```bash
docker exec pg-master psql -U admin -d crypto_db -c "\d investments"
```

### 4. Verificar tabla replicada en Replica:

```bash
docker exec pg-replica psql -U admin -d crypto_db -c "\d investments"
```

## 🎉 Estado Actual

✅ **Backend FastAPI**: Corriendo en `http://localhost:8000`  
✅ **CQRS Pattern**: Implementado correctamente  
✅ **Escrituras**: Van al Master DB (172.20.0.10)  
✅ **Lecturas**: Vienen de Replica DB (172.20.0.11)  
✅ **CoinGecko API**: Integrado y funcionando  
✅ **Replicación PostgreSQL**: Activa y sincronizada

## 🚀 Próximos Pasos Sugeridos

1. **Crear Frontend**: Desarrollar interfaz web para consumir la API
2. **Agregar más endpoints**:
   - `DELETE /invest/{id}` - Eliminar inversión
   - `PUT /invest/{id}` - Actualizar inversión
   - `GET /invest/{id}` - Ver inversión específica
3. **Implementar autenticación**: JWT tokens para seguridad
4. **Agregar validaciones**: Límites de inversión, montos mínimos, etc.
5. **Configurar CORS**: Para permitir acceso desde diferentes dominios
6. **Implementar cache**: Redis para cachear precios de criptomonedas
7. **Agregar tests**: Unit tests y integration tests
8. **Monitoreo**: Prometheus + Grafana para métricas

## 📝 Notas Importantes

> [!IMPORTANT]
> El servidor está configurado con `--reload`, lo que significa que se reiniciará automáticamente cuando detecte cambios en los archivos Python. Esto es ideal para desarrollo pero debe desactivarse en producción.

> [!WARNING]
> La replicación PostgreSQL es **asíncrona**, por lo que puede haber un pequeño retraso (milisegundos) entre que se escribe en el Master y se replica en la Réplica. En producción, esto es aceptable para la mayoría de los casos de uso.

> [!CAUTION]
> La API de CoinGecko tiene límites de rate limiting. Para uso en producción, considera implementar un sistema de caché para reducir las llamadas a la API.
