"""
quality_checks.py
------------------
Führt automatisierte Qualitätsprüfungen auf den in PostGIS gespeicherten
Gleisdaten durch:

  1. Lückenerkennung  – Endpunkte von Segmenten, die nahe beieinander liegen,
                         sich aber nicht berühren (mögliche Digitalisierungsfehler)
  2. Duplikaterkennung – (nahezu) identische Liniengeometrien
  3. Streckenlänge      – Gesamtlänge je Bahntyp (rail, tram, ...)
  4. Bahnhof-Abstand    – Bahnhöfe, die auffällig weit von jeder Gleislinie
                          entfernt liegen (mögliche Georeferenzierungsfehler)

Ergebnisse werden als CSV (output/qa_report.csv) und als GeoPackage
(output/qa_results.gpkg) gespeichert, damit du sie direkt in QGIS öffnen kannst.

Aufruf:
    python quality_checks.py
"""

import os
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
from config import SQLALCHEMY_URL, GAP_THRESHOLD_METERS, STATION_BUFFER_METERS

OUTPUT_DIR = "output"


def get_engine():
    return create_engine(SQLALCHEMY_URL)


# ---------------------------------------------------------------------------
# 1. Lückenerkennung: Endpunkte, die nahe sind, aber nicht verbunden
# ---------------------------------------------------------------------------
GAP_QUERY = """
WITH numbered AS (
    SELECT row_number() OVER () AS id, geom FROM gleis_segmente
),
endpoints AS (
    SELECT
        id,
        ST_StartPoint(geom) AS pt,
        'start' AS kind
    FROM numbered
    UNION ALL
    SELECT
        id,
        ST_EndPoint(geom) AS pt,
        'end' AS kind
    FROM numbered
)
SELECT
    a.id AS segment_a,
    b.id AS segment_b,
    ST_Distance(a.pt::geography, b.pt::geography) AS distanz_meter,
    ST_AsText(ST_Centroid(ST_Collect(a.pt, b.pt))) AS ungefaehre_position,
    ST_Collect(a.pt, b.pt) AS geom
FROM endpoints a
JOIN endpoints b
    ON a.id < b.id
    AND ST_DWithin(a.pt::geography, b.pt::geography, :threshold)
    AND NOT ST_Equals(a.pt, b.pt)
ORDER BY distanz_meter;
"""


def check_gaps(engine, threshold: float) -> gpd.GeoDataFrame:
    print(f"\n[1/4] Prüfe auf Lücken (< {threshold} m, aber nicht verbunden) ...")
    gdf = gpd.read_postgis(
        text(GAP_QUERY), engine, geom_col="geom", params={"threshold": threshold}
    )
    print(f"  -> {len(gdf)} potenzielle Lücken gefunden.")
    return gdf


# ---------------------------------------------------------------------------
# 2. Duplikaterkennung
# ---------------------------------------------------------------------------
DUPLICATE_QUERY = """
WITH numbered AS (
    SELECT row_number() OVER () AS id, geom FROM gleis_segmente
)
SELECT
    a.id AS segment_a,
    b.id AS segment_b,
    a.geom AS geom
FROM numbered a
JOIN numbered b
    ON a.id < b.id
    AND ST_Equals(a.geom, b.geom);
"""


def check_duplicates(engine) -> gpd.GeoDataFrame:
    print("\n[2/4] Prüfe auf doppelte Geometrien ...")
    gdf = gpd.read_postgis(text(DUPLICATE_QUERY), engine, geom_col="geom")
    print(f"  -> {len(gdf)} doppelte Segmente gefunden.")
    return gdf


# ---------------------------------------------------------------------------
# 3. Streckenlänge je Typ
# ---------------------------------------------------------------------------
LENGTH_QUERY = """
SELECT
    railway_type,
    COUNT(*) AS anzahl_segmente,
    ROUND((SUM(ST_Length(geom::geography)) / 1000)::numeric, 2) AS laenge_km
FROM gleis_segmente
GROUP BY railway_type
ORDER BY laenge_km DESC;
"""


def check_lengths(engine) -> pd.DataFrame:
    print("\n[3/4] Berechne Streckenlängen je Typ ...")
    df = pd.read_sql(text(LENGTH_QUERY), engine)
    print(df.to_string(index=False))
    return df


# ---------------------------------------------------------------------------
# 4. Bahnhöfe weit entfernt von jeder Gleislinie
# ---------------------------------------------------------------------------
STATION_DISTANCE_QUERY = """
WITH numbered AS (
    SELECT row_number() OVER () AS id, name, geom FROM bahnhoefe
)
SELECT
    b.id AS bahnhof_id,
    b.name,
    (
        SELECT MIN(ST_Distance(b.geom::geography, g.geom::geography))
        FROM gleis_segmente g
    ) AS abstand_zur_naechsten_strecke_m,
    b.geom AS geom
FROM numbered b
ORDER BY abstand_zur_naechsten_strecke_m DESC;
"""


def check_station_distance(engine, threshold: float) -> gpd.GeoDataFrame:
    print(f"\n[4/4] Prüfe Bahnhöfe mit Abstand > {threshold} m zur nächsten Strecke ...")
    gdf = gpd.read_postgis(text(STATION_DISTANCE_QUERY), engine, geom_col="geom")
    flagged = gdf[gdf["abstand_zur_naechsten_strecke_m"] > threshold]
    print(f"  -> {len(flagged)} von {len(gdf)} Bahnhöfen auffällig weit entfernt.")
    return gdf


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()

    gaps = check_gaps(engine, GAP_THRESHOLD_METERS)
    duplicates = check_duplicates(engine)
    lengths = check_lengths(engine)
    stations = check_station_distance(engine, STATION_BUFFER_METERS)

    # CSV-Zusammenfassung (ohne Geometrie, für schnellen Überblick)
    summary_rows = [
        {"pruefung": "Lücken (< Schwellenwert, nicht verbunden)", "anzahl_treffer": len(gaps)},
        {"pruefung": "Doppelte Geometrien", "anzahl_treffer": len(duplicates)},
        {"pruefung": "Bahnhöfe weit von Strecke entfernt", "anzahl_treffer": int((stations["abstand_zur_naechsten_strecke_m"] > STATION_BUFFER_METERS).sum())},
    ]
    pd.DataFrame(summary_rows).to_csv(f"{OUTPUT_DIR}/qa_report.csv", index=False)
    lengths.to_csv(f"{OUTPUT_DIR}/streckenlaengen.csv", index=False)

    # GeoPackage mit allen Layern für QGIS
    gpkg_path = f"{OUTPUT_DIR}/qa_results.gpkg"
    if len(gaps) > 0:
        gaps.to_file(gpkg_path, layer="luecken", driver="GPKG")
    if len(duplicates) > 0:
        duplicates.to_file(gpkg_path, layer="duplikate", driver="GPKG")
    stations.to_file(gpkg_path, layer="bahnhof_abstand", driver="GPKG")

    print(f"\nFertig. Ergebnisse in '{OUTPUT_DIR}/qa_report.csv' und '{gpkg_path}'.")
    print("Öffne die .gpkg-Datei in QGIS, um die Ergebnisse auf der Karte zu sehen.")


if __name__ == "__main__":
    main()