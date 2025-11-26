#!/bin/bash
# ============================================
# Entrypoint completo para PostgreSQL Replica
# ============================================

set -e

echo "🔄 Iniciando configuración de PostgreSQL Replica..."

# Esperar a que el master esté listo
echo "⏳ Esperando a que el Master esté disponible..."
until PGPASSWORD=$MASTER_DB_PASSWORD psql -h "$MASTER_HOST" -U $MASTER_DB_USER -d crypto_db -c '\q' 2>/dev/null; do
  echo "   Master no disponible todavía, reintentando en 2 segundos..."
  sleep 2
done

echo "✅ Master está disponible"

# Verificar si ya existe data (evitar reinicialización)
if [ -s "$PGDATA/PG_VERSION" ]; then
    echo "⚠️  Réplica ya inicializada, iniciando PostgreSQL en modo réplica..."
    chown -R postgres:postgres $PGDATA 2>/dev/null || true
    exec gosu postgres postgres
fi

echo "🚀 Realizando backup base desde el Master..."

# Asegurarse de que el directorio esté vacío
rm -rf $PGDATA/*

# Realizar backup base desde el master
PGPASSWORD=$MASTER_PASSWORD pg_basebackup \
    -h $MASTER_HOST \
    -D $PGDATA \
    -U $MASTER_USER \
    -Fp \
    -Xs \
    -P \
    -R

echo "✅ Backup base completado"

# Configurar parámetros adicionales para la réplica
cat >> $PGDATA/postgresql.auto.conf <<EOF
# Configuración de réplica
hot_standby = on
max_standby_streaming_delay = 30s
wal_receiver_status_interval = 10s
hot_standby_feedback = on
EOF

echo "📝 Configuración de réplica aplicada"
echo "🎉 Réplica configurada correctamente"
echo "🔄 Iniciando servidor PostgreSQL en modo réplica..."

# Asegurar permisos correctos
chown -R postgres:postgres $PGDATA
chmod 700 $PGDATA

# Iniciar PostgreSQL como usuario postgres
exec gosu postgres postgres
