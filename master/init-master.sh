#!/bin/bash
# ============================================
# Script de Inicialización PostgreSQL Master
# ============================================

set -e

echo "🔧 Inicializando PostgreSQL Master..."

# Crear usuario de replicación
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Crear usuario de replicación
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password_2024';
    
    -- Otorgar permisos necesarios
    GRANT CONNECT ON DATABASE crypto_db TO replicator;
    
    -- Crear tabla de ejemplo para probar replicación
    CREATE TABLE IF NOT EXISTS test_replication (
        id SERIAL PRIMARY KEY,
        mensaje VARCHAR(100),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Insertar datos de prueba
    INSERT INTO test_replication (mensaje) VALUES 
        ('Replicación PostgreSQL funcionando!'),
        ('Datos del Master'),
        ('Sistema Distribuido Activo');
    
    -- Mostrar información
    SELECT 'Master inicializado correctamente' as status;
EOSQL

echo "✅ PostgreSQL Master inicializado correctamente"
echo "📊 Usuario de replicación 'replicator' creado"
echo "🔄 Listo para aceptar conexiones de réplica"
