#!/bin/bash
set -e

echo "Initializing weather database..."

# Création de l'utilisateur s'il n'existe pas
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
            CREATE USER airflow WITH PASSWORD 'airflow';
        END IF;
    END
    \$\$;
EOSQL

# Création de la base de données si elle n'existe pas
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'weather_data') THEN
            CREATE DATABASE weather_data;
        END IF;
    END
    \$\$;

    -- Attribution des droits sur la base de données à l'utilisateur airflow
    GRANT ALL PRIVILEGES ON DATABASE weather_data TO airflow;
EOSQL

echo "Weather database initialization completed!"