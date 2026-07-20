"""
load_data.py
------------
Lädt Bahnstrecken- und Bahnhof-Daten von OpenStreetMap (via osmnx/Overpass API)
für das in config.py definierte Gebiet und schreibt sie in die PostGIS-Datenbank.

Aufruf:
    python load_data.py
"""

import osmnx as ox
import geopandas as gpd
from sqlalchemy import create_engine
from config import SEARCH_AREA, SQLALCHEMY_URL

ox.settings.log_console = True
ox.settings.use_cache = True


def fetch_railway_lines(place: str) -> gpd.GeoDataFrame:
    """Holt alle Bahnstrecken-Linien (railway=rail/light_rail/tram) für das Gebiet."""
    print(f"Lade Gleisdaten für: {place} ...")
    tags = {"railway": ["rail", "light_rail", "tram", "narrow_gauge"]}
    gdf = ox.features_from_place(place, tags)
    gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])].copy()
    gdf = gdf.explode(index_parts=False)  # MultiLineString -> einzelne LineStrings
    gdf = gdf.reset_index()
    print(f"  -> {len(gdf)} Gleissegmente gefunden.")
    return gdf


def fetch_stations(place: str) -> gpd.GeoDataFrame:
    """Holt alle Bahnhöfe/Haltestellen (railway=station/halt) für das Gebiet."""
    print(f"Lade Bahnhofsdaten für: {place} ...")
    tags = {"railway": ["station", "halt"]}
    gdf = ox.features_from_place(place, tags)
    gdf = gdf[gdf.geometry.type == "Point"].copy()
    gdf = gdf.reset_index()
    print(f"  -> {len(gdf)} Bahnhöfe/Haltestellen gefunden.")
    return gdf


def write_to_postgis(gleis_gdf: gpd.GeoDataFrame, bahnhof_gdf: gpd.GeoDataFrame):
    engine = create_engine(SQLALCHEMY_URL)

    gleis_out = gpd.GeoDataFrame(
        {
            "osm_id": gleis_gdf.get("osmid", gleis_gdf.index),
            "railway_type": gleis_gdf.get("railway", "unknown"),
            "name": gleis_gdf.get("name", None),
            "geom": gleis_gdf.geometry,
        },
        geometry="geom",
        crs="EPSG:4326",
    )
    gleis_out.to_postgis("gleis_segmente", engine, if_exists="replace", index=False)
    print(f"{len(gleis_out)} Gleissegmente in PostGIS geschrieben (Tabelle: gleis_segmente).")

    bahnhof_out = gpd.GeoDataFrame(
        {
            "osm_id": bahnhof_gdf.get("osmid", bahnhof_gdf.index),
            "name": bahnhof_gdf.get("name", None),
            "geom": bahnhof_gdf.geometry,
        },
        geometry="geom",
        crs="EPSG:4326",
    )
    bahnhof_out.to_postgis("bahnhoefe", engine, if_exists="replace", index=False)
    print(f"{len(bahnhof_out)} Bahnhöfe in PostGIS geschrieben (Tabelle: bahnhoefe).")


if __name__ == "__main__":
    gleis_gdf = fetch_railway_lines(SEARCH_AREA)
    bahnhof_gdf = fetch_stations(SEARCH_AREA)
    write_to_postgis(gleis_gdf, bahnhof_gdf)
    print("\nFertig. Weiter mit: python quality_checks.py")
