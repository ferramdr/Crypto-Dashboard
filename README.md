# Proyecto Sistemas Distribuidos - PostgreSQL Master-Replica

## 📋 Descripción

Proyecto universitario de Sistemas Distribuidos con arquitectura de replicación PostgreSQL:

- **pg-master**: PostgreSQL 15 (Servidor maestro para escritura)
- **pg-replica**: PostgreSQL 15 (Servidor réplica para lectura)
- **pgadmin**: Panel de administración web

## 🌐 Arquitectura de Red

- **Red**: `distribuidos-net` (bridge)
- **Subred**: `172.20.0.0/16`
- **Gateway**: `172.20.0.1`

### Asignación de IPs Estáticas:

| Servicio   | IP Estática | Puerto Host | Puerto Contenedor |
| ---------- | ----------- | ----------- | ----------------- |
| pg-master  | 172.20.0.10 | 5432        | 5432              |
| pg-replica | 172.20.0.11 | 5433        | 5432              |
| pgadmin    | 172.20.0.5  | 5050        | 80                |

## 📁 Estructura del Proyecto

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

## 🚀 Inicio Rápido

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

### pgAdmin:

- **Email**: `admin@admin.com`
- **Password**: `admin`

## 🛠️ Comandos Útiles

### Ver logs en tiempo real

```powershell
docker compose logs -f pg-master
docker compose logs -f pg-replica
docker compose logs -f pgadmin
```

### Verificar estado de contenedores

```powershell
docker compose ps
```

### Detener servicios

```powershell
docker compose down
```

### Detener y eliminar volúmenes (⚠️ Elimina todos los datos)

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

## ⚠️ Problemas Comunes

### Error: "exec user process caused: no such file or directory"

**Causa**: Los archivos `.sh` tienen saltos de línea de Windows (CRLF) en lugar de Unix (LF).

**Solución**:

1. Abre `replica/entrypoint.sh` en VS Code
2. En la esquina inferior derecha, haz clic en "CRLF"
3. Selecciona "LF"
4. Guarda el archivo
5. Repite para `master/init-master.sh`
6. Ejecuta: `docker compose down -v && docker compose up --build`

### Docker no reconocido

**Solución**: Instala Docker Desktop desde https://www.docker.com/products/docker-desktop/

### pgAdmin no carga

**Solución**: Espera 15-20 segundos después de `docker compose up`. pgAdmin tarda en inicializar.

## 📚 Conceptos Implementados

- ✅ **Replicación Streaming**: Sincronización en tiempo real
- ✅ **Write-Ahead Logging (WAL)**: Mecanismo de replicación de PostgreSQL
- ✅ **High Availability**: Datos replicados para redundancia
- ✅ **Read Scaling**: Distribuir lecturas en la réplica
- ✅ **Hot Standby**: Réplica disponible para consultas de solo lectura

## 📖 Referencias

- [PostgreSQL Replication](https://www.postgresql.org/docs/15/high-availability.html)
- [Docker Compose](https://docs.docker.com/compose/)
- [pgAdmin](https://www.pgadmin.org/docs/)

---

**¡Proyecto listo para demostración y presentación universitaria!** 🎓🚀
