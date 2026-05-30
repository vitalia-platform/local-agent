#!/usr/bin/env bash

set -e

# Default values if not provided via .env
DB_CONTAINER=${DB_CONTAINER_NAME:-vitalia_db}
DB_USER=${POSTGRES_USER:-vitalia_admin}
DB_NAME=${POSTGRES_DB:-vitalia_db}
SCHEMA_FILE="scripts/schema.sql"

echo "⏳ Aguardando o PostgreSQL no container '$DB_CONTAINER' iniciar..."
# Pinga até que o pg_isready responda com sucesso
until docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
    echo "   ...banco de dados ainda não está pronto. Tentando novamente em 2 segundos."
    sleep 2
done

echo "✅ PostgreSQL está pronto."

echo "💉 Aplicando schema de dados e extensões (vector, uuid)..."
if [ -f "$SCHEMA_FILE" ]; then
    docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$SCHEMA_FILE"
    echo "✅ Schema aplicado com sucesso!"
else
    echo "❌ Erro: Arquivo '$SCHEMA_FILE' não encontrado."
    exit 1
fi
