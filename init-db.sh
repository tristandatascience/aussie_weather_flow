#!/bin/bash
set -e

# Créer la base de données 'weather_data'
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE DATABASE weather_data;
EOSQL