# Proyecto Sistemas Distribuidos - PostgreSQL Master-Replica

## Descripción

### English

This project demonstrates a PostgreSQL master-replica deployment used by a small Crypto Dashboard application. The repository contains Docker Compose configurations, initialization scripts, and sample code that run a FastAPI backend and a Streamlit dashboard inside containers. The setup automates a streaming replication topology (master -> replica) and provides tools to verify replication, manage the services with Docker Compose, and inspect the databases using pgAdmin.

Key features:

- Automated PostgreSQL master/replica setup using Docker
- Streaming replication with WAL shipping and hot standby
- FastAPI backend serving an API (docs at /docs)
- Streamlit-based dashboard for visualizing crypto data
- pgAdmin included for database management
- Scripts and examples to test replication and manage lifecycle

This project is intended for development, testing, and educational purposes to explore high-availability concepts, replication, and read-scaling with a replica. Do NOT use the provided credentials or configuration in production.

---

## Cómo Ejecutar el Proyecto

### Paso 1: Abrir los Contenedores en Docker

```powershell
# Navega al directorio del proyecto
cd "d:\Ferram\Personal\Crypto Dashboard"

# Levanta todos los contenedores
docker compose up -d --build
```

> **Nota**: El proceso puede tardar 30-60 segundos mientras se inicializan los contenedores y se configura la replicación.

### Paso 2: Verificar que los Contenedores Estén Corriendo

```powershell
docker compose ps
```

### Paso 3: Instalar Dependencias en el Contenedor Web

```powershell
# Accede al contenedor web-app
docker exec -it web-app bash

# Dentro del contenedor, instala las dependencias
pip install -r requirements.txt

# Sal del contenedor
exit
```

### Paso 4: Iniciar el API Backend

```powershell
# Inicia FastAPI en segundo plano
docker exec -d web-app uvicorn main:app --host 0.0.0.0 --port 8000
```

### Paso 5: Iniciar el Dashboard Web

```powershell
# Inicia Streamlit en segundo plano
docker exec -d web-app streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### Paso 6: Abrir la Aplicación en el Navegador

**Dashboard**: http://localhost:8501
**API Docs**: http://localhost:8000/docs
**pgAdmin**: http://localhost:5050

**Credenciales de pgAdmin:**

- Email: `admin@admin.com`
- Password: `admin`

### Paso 7: Detener y Reiniciar el Proyecto

#### Detener normalmente (MANTIENE los datos)

```powershell
# Detener todos los contenedores
docker compose down
```

Qué hace:

- Detiene todos los contenedores
- **Mantiene los volúmenes** (tus datos persisten)
- Al volver a levantar con `docker compose up -d`, continúa desde donde quedó

#### **Reiniciar el proyecto (sin perder datos)**

```powershell
# Detener
docker compose down

# Esperar 2-3 segundos

# Levantar nuevamente
docker compose up -d
```

**La réplica automáticamente:**

- Verifica si tiene datos válidos
- Continúa la replicación desde donde quedó
- Se re-sincroniza solo si es necesario

#### **Reinicio completo (ELIMINA todos los datos)**

Solo usa esto si:

- Tienes problemas de sincronización
- Quieres empezar desde cero
- Estás probando cambios en la configuración

```powershell
# Detener Y eliminar volúmenes
docker compose down -v

# Levantar nuevamente (empezará desde cero)
docker compose up -d
```

**ADVERTENCIA**: Este comando eliminará TODOS los datos de las bases de datos.

---

## Arquitectura de Red

- **Red**: `distribuidos-net` (bridge)
- **Subred**: `172.20.0.0/16`
- **Gateway**: `172.20.0.1`

## Estructura del Proyecto

```
Cypto Dashboard/
├── docker-compose.yml          # Configuración principal de Docker Compose
├── README.md                   # Este archivo
├── GUIA_RAPIDA.md             # Guía paso a paso detallada
│
├── master/                     # Configuración PostgreSQL Master
│   ├── postgresql.conf        # Configuración del servidor
│   ├── pg_hba.conf           # Autenticación
│   └── init-master.sh        # Script de inicialización
│
└── replica/                    # Configuración PostgreSQL Replica
    └── entrypoint.sh          # Script de replicación automática
```

## Inicio Rápido

### 1. Levantar los contenedores

```bash
# Docker Compose v2 (Plugin)
docker compose up --build

# Docker Compose v1 (Standalone)
docker-compose up --build
```

### 2. Acceder a pgAdmin

- URL: http://localhost:5050
- Email: `admin@admin.com`
- Password: `admin`

### 3. Configurar servidores en pgAdmin

**Maestro (Escritura):**

- Host: `172.20.0.10`
- Usuario: `admin`
- Password: `root_password`

**Réplica (Lectura):**

- Host: `172.20.0.11`
- Usuario: `ferram`
- Password: `Bean2023`

## 🔄 Cómo Funciona la Replicación

1. **pg-master** inicia y crea:

   - Usuario de replicación `replicator`
   - Base de datos `crypto_db`
   - Tabla de prueba con datos iniciales

2. **pg-replica** espera al master y luego:

   - Realiza un backup base completo (pg_basebackup)
   - Se configura automáticamente como réplica streaming
   - Sincroniza cambios en tiempo real

3. **Resultado**: Cualquier cambio en el master aparece automáticamente en la réplica

## ✅ Verificar Replicación

### Desde la terminal:

```powershell
# Insertar en el Master
docker exec -it pg-master psql -U admin -d crypto_db -c "INSERT INTO test_replication (mensaje) VALUES ('Test desde Master');"

# Verificar en la Réplica
docker exec -it pg-replica psql -U admin -d crypto_db -c "SELECT * FROM test_replication;"
```

### Ver estado de replicación:

```powershell
# En el Master - Ver réplicas conectadas
docker exec -it pg-master psql -U admin -d crypto_db -c "SELECT * FROM pg_stat_replication;"

# En la Réplica - Ver estado de recepción
docker exec -it pg-replica psql -U admin -d crypto_db -c "SELECT * FROM pg_stat_wal_receiver;"
```

## 🔑 Credenciales

**⚠️ ADVERTENCIA**: Estas son credenciales de desarrollo. **NO usar en producción**.

### PostgreSQL Master:

- **User**: `admin`
- **Password**: `root_password`
- **Database**: `crypto_db`

### PostgreSQL Replica:

- **User**: `ferram`
- **Password**: `Bean2023`

### Usuario de Replicación:

- **User**: `replicator`
- **Password**: `repl_password_2024`

### Verificar estado de contenedores

```powershell
docker compose ps
```

### Detener servicios

```powershell
docker compose down
```

### Detener y eliminar volúmenes (Elimina todos los datos)

```powershell
docker compose down -v
```

### Conectarse directamente a PostgreSQL

```powershell
# Master
docker exec -it pg-master psql -U admin -d crypto_db

# Replica
docker exec -it pg-replica psql -U ferram -d crypto_db
```

### Reiniciar un servicio específico

```powershell
docker compose restart pg-master
```

## Conceptos Implementados

- **Replicación Streaming**: Sincronización en tiempo real
- **Write-Ahead Logging (WAL)**: Mecanismo de replicación de PostgreSQL
- **High Availability**: Datos replicados para redundancia
- **Read Scaling**: Distribuir lecturas en la réplica
- **Hot Standby**: Réplica disponible para consultas de solo lectura

---
