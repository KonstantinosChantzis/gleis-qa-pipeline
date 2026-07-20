-- Führe dies aus mit: psql -U postgres -f setup_db.sql

DROP DATABASE IF EXISTS gleis_qa;
CREATE DATABASE gleis_qa;

\c gleis_qa

CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabelle für Bahnstrecken-Segmente (wird von load_data.py befüllt)
CREATE TABLE IF NOT EXISTS gleis_segmente (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT,
    railway_type VARCHAR(50),
    name VARCHAR(255),
    geom GEOMETRY(LineString, 4326)
);

-- Tabelle für Bahnhöfe/Stationen
CREATE TABLE IF NOT EXISTS bahnhoefe (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT,
    name VARCHAR(255),
    geom GEOMETRY(Point, 4326)
);

-- Räumliche Indizes für schnellere Abfragen
CREATE INDEX IF NOT EXISTS idx_gleis_geom ON gleis_segmente USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_bahnhoefe_geom ON bahnhoefe USING GIST (geom);

SELECT 'Datenbank gleis_qa erfolgreich eingerichtet.' AS status;
