# 🚀 Sistema Distribuido de Cripto-Inversiones

## 1. Flujo de Operación del Sistema

### Perspectiva del Usuario y Flujo de Datos

El sistema opera mediante una arquitectura de 3 capas con segregación de responsabilidades (CQRS), permitiendo un flujo bidireccional optimizado:

#### **Inicio de Sesión - Acceso al Dashboard**

1. El usuario accede a la interfaz web desarrollada en **Streamlit** (Nodo Frontend - `172.20.0.2`).
2. El navegador establece una conexión HTTP con el servidor Streamlit ejecutándose en el contenedor Docker aislado.
3. La interfaz se renderiza mostrando dos paneles principales: **Escritura de Inversiones** y **Consulta de Historial**.

#### **Flujo de Comando - Registro de Inversión (Escritura)**

Cuando el usuario registra una nueva inversión:

1. **Capa de Presentación (Frontend):**

   - El usuario completa el formulario con los datos de la inversión (nombre de la criptomoneda, monto en USD).
   - Al presionar "Registrar", el componente Streamlit serializa los datos en formato JSON.

2. **Capa de Aplicación (Backend API):**

   - Se emite una petición **HTTP POST** a `http://backend:8000/invest` a través de la red interna privada `distribuidos-net`.
   - El servidor **FastAPI** recibe la solicitud en el endpoint de comando (`/invest`).
   - El controlador de comandos valida los datos y consulta la API externa de **CoinGecko** (HTTPS/REST) para obtener el precio actual de la criptomoneda.

3. **Capa de Persistencia (Base de Datos Maestro):**

   - La transacción se dirige exclusivamente al **Nodo Maestro PostgreSQL** (`172.20.0.10`).
   - **SQLAlchemy ORM** ejecuta un INSERT en la tabla `investments` del esquema maestro.
   - PostgreSQL confirma la transacción con un COMMIT, garantizando consistencia ACID.

4. **Confirmación al Usuario:**
   - El backend responde con HTTP 200 y un mensaje de éxito.
   - El frontend muestra: _"✅ Datos escritos en NODO MAESTRO (172.20.0.10)"_.

#### **Flujo de Consulta - Visualización del Historial (Lectura)**

Cuando el usuario solicita visualizar el historial de inversiones:

1. **Capa de Presentación (Frontend):**

   - El usuario presiona el botón "Actualizar Datos" en el panel de lectura.
   - Se dispara una petición **HTTP GET** a `http://backend:8000/history`.

2. **Capa de Aplicación (Backend API):**

   - El servidor FastAPI recibe la solicitud en el endpoint de consulta (`/history`).
   - El controlador de consultas accede **exclusivamente** a la **Base de Datos Réplica** (`172.20.0.11`).

3. **Capa de Persistencia (Base de Datos Réplica):**

   - SQLAlchemy ejecuta un SELECT sobre la tabla replicada `investments`.
   - La réplica responde con los datos históricos sin afectar la carga del nodo maestro.

4. **Renderizado en Frontend:**
   - El backend serializa los resultados en formato JSON y responde con HTTP 200.
   - Streamlit renderiza una tabla (`st.dataframe`) con el historial.
   - Se muestra el indicador: _"📡 Leyendo datos del NODO RÉPLICA (172.20.0.11)"_.
   - Se genera un gráfico de evolución (`st.line_chart`) con los valores históricos.

#### **Sincronización Interna - Replicación Maestro → Réplica**

El sistema mantiene **sincronización continua y automática** entre los nodos de base de datos:

- **PostgreSQL Streaming Replication** opera en segundo plano mediante el protocolo WAL (Write-Ahead Logging).
- Cada transacción confirmada en el nodo maestro genera registros WAL que se transmiten vía **TCP/IP** al nodo réplica.
- El nodo réplica aplica los cambios de forma asíncrona, manteniendo una copia actualizada con latencia mínima (<100ms en condiciones normales).
- Esta arquitectura garantiza **alta disponibilidad (HA)**: si el maestro falla, la réplica puede promovida a maestro (failover manual o automático con herramientas como Patroni).

---

## 2. Análisis de Puntos Fuertes - Infraestructura y Resiliencia

### **Arquitectura Basada en Nodos Independientes**

El sistema implementa una **simulación realista de infraestructura distribuida** mediante la virtualización de nodos independientes con **Docker y Docker Compose**. Esta arquitectura replica fielmente un entorno de producción multi-servidor:

#### **Nodo 1: Frontend (Streamlit) - `172.20.0.2`**

- **Función:** Capa de presentación para interacción usuario-sistema.
- **Tecnología:** Python 3.11, Streamlit, Requests.
- **Aislamiento:** Contenedor Docker con imagen base `python:3.11-slim`.
- **Persistencia:** Sin estado; toda la data se gestiona en los nodos de backend y base de datos.
- **Ventaja:** Escalabilidad horizontal mediante réplicas del contenedor (balanceo de carga con Nginx/Traefik en producción).

#### **Nodo 2: Backend (FastAPI) - `172.20.0.3`**

- **Función:** Capa de lógica de negocio y orchestration de comandos/consultas (CQRS).
- **Tecnología:** FastAPI, Uvicorn ASGI Server, SQLAlchemy 2.x, Pydantic.
- **Aislamiento:** Contenedor independiente con endpoints REST expuestos en el puerto 8000.
- **Conexión a BD:** Doble conexión configurada:
  - `MASTER_DB_URL` → Escrituras (comandos).
  - `REPLICA_DB_URL` → Lecturas (consultas).
- **Ventaja:** Separación de responsabilidades permite optimización granular (cache en réplica, índices específicos).

#### **Nodo 3: Base de Datos Maestro (PostgreSQL Master) - `172.20.0.10`**

- **Función:** Nodo de escritura principal (CRUD operations - Create, Update, Delete).
- **Tecnología:** PostgreSQL 15 con extensión de replicación configurada.
- **Configuración Crítica:**
  - `wal_level = replica`: Habilita el registro detallado de transacciones.
  - `max_wal_senders = 3`: Permite hasta 3 réplicas simultáneas.
  - `archive_mode = on`: Archiva WAL para recuperación ante desastres.
- **Persistencia:** Volume Docker `pg_master_data` garantiza durabilidad de datos.
- **Ventaja:** Point-in-Time Recovery (PITR) mediante WAL archiving.

#### **Nodo 4: Base de Datos Réplica (PostgreSQL Replica) - `172.20.0.11`**

- **Función:** Nodo de lectura (queries, reporting, analytics).
- **Tecnología:** PostgreSQL 15 en modo Hot Standby (read-only).
- **Configuración Crítica:**
  - `hot_standby = on`: Permite consultas mientras recibe datos del maestro.
  - `primary_conninfo`: String de conexión al nodo maestro para streaming replication.
- **Persistencia:** Volume independiente `pg_replica_data`.
- **Ventaja:** Distribución de carga de lectura; tolerancia a fallos (disaster recovery standby).

### **Replicación de Base de Datos - Tolerancia a Fallos y Alta Disponibilidad**

La implementación de **PostgreSQL Streaming Replication** constituye el pilar fundamental de la resiliencia del sistema:

#### **Mecanismo de Replicación**

- **Streaming Replication:** El maestro transmite cambios WAL en tiempo real al nodo réplica mediante conexión TCP persistente.
- **Replicación Asíncrona:** Mejor performance (el maestro no espera confirmación de la réplica para hacer COMMIT).
- **Replicación Síncrona (Opcional):** Configurable para escenarios de zero data loss (requisito: `synchronous_commit = on`).

#### **Garantías de Disponibilidad**

- **Lectura Continua:** La réplica puede servir queries incluso si el maestro está bajo mantenimiento.
- **Failover Manual:** En caso de fallo del maestro, la réplica puede ser promovida con el comando `pg_ctl promote`.
- **Recuperación ante Desastres:** Los archivos WAL permiten restaurar el sistema a cualquier punto en el tiempo (RPO <1 minuto).

#### **Ventajas Operacionales**

- **Escalabilidad de Lectura:** Se pueden añadir múltiples réplicas para distribuir consultas pesadas (reports, analytics).
- **Testing Seguro:** Las consultas complejas pueden ejecutarse en la réplica sin riesgo de afectar al maestro.
- **Backup en Caliente:** La réplica puede usarse como origen para backups sin impactar la performance de escritura.

### **Aislamiento y Seguridad de Red**

El sistema implementa **segmentación de red** mediante una red privada de Docker:

#### **Red Privada `distribuidos-net`**

- **Tipo:** Bridge network con driver bridge.
- **Subnet:** `172.20.0.0/16` (65,534 direcciones IP disponibles).
- **Ventaja:** Los contenedores solo son accesibles entre sí; el exterior no puede acceder directamente a las bases de datos.

#### **Asignación Estática de IPs**

- Garantiza direcciones predecibles para configuración de conexiones.
- Simplifica troubleshooting y monitorización de red.
- Permite implementar firewalls granulares (iptables rules) si se migra a Kubernetes.

#### **Volúmenes Persistentes**

- **`pg_master_data`** y **`pg_replica_data`:** Garantizan persistencia de datos entre reinicios de contenedores.
- **Ventaja:** Supervivencia de datos ante fallos de contenedores; portabilidad mediante volume backups.

---

## 3. Características Generales del Sistema

### **Arquitectura y Patrones de Diseño**

- ✅ **Patrón CQRS (Command Query Responsibility Segregation):**

  - Segregación completa de operaciones de escritura (comandos) y lectura (consultas).
  - Comandos dirigidos al nodo maestro; consultas dirigidas a la réplica.
  - Optimización independiente de cada ruta de acceso a datos.

- ✅ **Arquitectura de 3 Capas (Three-Tier Architecture):**

  - **Capa de Presentación:** Streamlit (Frontend).
  - **Capa de Lógica de Negocio:** FastAPI (Backend/API).
  - **Capa de Datos:** PostgreSQL Master-Replica.

- ✅ **Infraestructura como Código (IaC):**
  - Definición completa del sistema en `docker-compose.yml`.
  - Reproducibilidad total: deployment de toda la infraestructura con un solo comando (`docker-compose up`).

### **Stack Tecnológico**

#### **Backend y API**

- **Lenguaje:** Python 3.11 (performance mejorado, mejor typing support).
- **Framework Web:** FastAPI (async/await nativo, auto-generación de documentación OpenAPI).
- **ASGI Server:** Uvicorn (alta concurrencia mediante event loop).
- **ORM:** SQLAlchemy 2.x (soporte SQL moderno, mejor performance).
- **Validación:** Pydantic v2 (validación de datos en runtime con type hints).

#### **Frontend**

- **Framework:** Streamlit (rapid prototyping, widgets interactivos).
- **Client HTTP:** Requests (REST API consumption).

#### **Base de Datos**

- **SGBD:** PostgreSQL 15 (ACID compliance, extensiones avanzadas).
- **Replicación:** Streaming Replication (WAL-based).
- **Persistencia:** Docker Named Volumes.

#### **Infraestructura**

- **Containerización:** Docker 24.x, Docker Compose v2.
- **Networking:** Docker Bridge Network con subnet privada.

### **Protocolos de Comunicación**

- **HTTP/REST:** Comunicación Frontend ↔ Backend (JSON serialization).
- **TCP/IP:** Comunicación Backend ↔ PostgreSQL (protocolo nativo PostgreSQL).
- **TCP/IP Streaming:** Replicación Maestro → Réplica (WAL streaming).
- **HTTPS/TLS:** Comunicación con API externa CoinGecko (seguridad de datos en tránsito).

### **Atributos de Calidad**

#### **Disponibilidad (Availability)**

- Replicación de base de datos garantiza lectura continua.
- Failover manual disponible en caso de fallo del maestro.
- RTO (Recovery Time Objective): <5 minutos.
- RPO (Recovery Point Objective): <1 minuto.

#### **Escalabilidad (Scalability)**

- **Horizontal:** Posibilidad de agregar múltiples réplicas de lectura.
- **Vertical:** Recursos de contenedores ajustables (CPU limits, memory limits).
- **Teórica:** Migración a Kubernetes para auto-scaling basado en métricas.

#### **Portabilidad (Portability)**

- Sistema completamente containerizado: ejecución en cualquier plataforma con Docker (Linux, Windows, macOS).
- Sin dependencias del sistema operativo host.
- Deployment reproducible en entornos cloud (AWS ECS, Google Cloud Run, Azure Container Instances).

#### **Rendimiento (Performance)**

- Backend asíncrono con FastAPI/Uvicorn (manejo de múltiples requests concurrentes).
- Separación de lectura/escritura evita contención en la base de datos.
- Índices optimizados en tablas para queries frecuentes.

#### **Mantenibilidad (Maintainability)**

- Código modular con separación clara de responsabilidades.
- Type hints completos en Python (mejor IDE support, menos bugs).
- Logs estructurados para debugging y monitorización.

#### **Seguridad (Security)**

- Red privada aislada (bases de datos no expuestas a internet).
- Credenciales gestionadas mediante variables de entorno (no hard-coded).
- Validación de inputs con Pydantic (prevención de SQL injection, XSS).

### **Funcionalidades Implementadas**

- 📊 **Registro de Inversiones:** Captura de inversiones con validación de datos y cotización en tiempo real.
- 📈 **Visualización de Historial:** Tabla interactiva y gráfico de evolución temporal.
- 🔄 **Sincronización Automática:** Replicación continua Maestro → Réplica sin intervención manual.
- 🌐 **Integración con API Externa:** Consulta de precios de criptomonedas vía CoinGecko API.
- 💾 **Persistencia Robusta:** Datos protegidos en volúmenes Docker con soporte para backups.
- 🖥️ **Interfaz Intuitiva:** Dashboard web responsive con feedback visual del estado del sistema.

---

## 📝 Notas Académicas

**Objetivo Pedagógico:** Este proyecto demuestra la implementación práctica de conceptos avanzados de sistemas distribuidos, incluyendo replicación de datos, patrones de arquitectura modernos (CQRS), y virtualización de infraestructura mediante contenedores.

**Justificación Técnica:** La elección de PostgreSQL Streaming Replication sobre soluciones como sharding o particionamiento se fundamenta en los requisitos de consistencia eventual y disponibilidad de lectura del sistema. El patrón CQRS maximiza el throughput al eliminar la contención entre operaciones de lectura y escritura en el mismo nodo.

**Escalabilidad Futura:** El sistema está diseñado para migración a arquitecturas de microservicios (separación de servicios de Investment, Pricing, Reporting) y orquestación con Kubernetes para alta disponibilidad en producción.
