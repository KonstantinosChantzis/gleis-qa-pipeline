# Gleis QA Pipeline (Python + PostGIS)

A portfolio project for quality-checking railway geodata. Downloads railway
track and station data from OpenStreetMap (Overpass API), loads it into a
PostGIS database, and runs automated data-quality checks — the same kind of
task performed professionally in railway surveying and utility geodata
management, built here end-to-end as a personal project.

## What this project does

1. Downloads railway line and station data from OpenStreetMap for an area of
   your choice (e.g. Essen, Germany)
2. Loads the data into a local **PostGIS** database
3. Runs automated quality checks:
   - Gap detection: track segments that should connect but don't
   - Duplicate detection: (near-)identical line geometries
   - Total network length by railway type
   - Buffer analysis: stations that are unexpectedly far from any track
4. Exports the results as a GeoPackage/CSV, ready to open in QGIS

## Tech stack

- **Python** (geopandas, osmnx, SQLAlchemy, psycopg2)
- **PostgreSQL / PostGIS** for spatial data storage and SQL-based analysis
- **QGIS** for visualizing the results

## Setup

### 1. Install prerequisites (one-time)

- **PostgreSQL** (includes PostGIS via the Stack Builder during installation):
  https://www.postgresql.org/download/
- **Python 3.11+**: https://www.python.org/downloads/

### 2. Create the database

```bash
psql -U postgres -f setup_db.sql
```

This creates the `gleis_qa` database, enables the PostGIS extension, and
creates the two tables used by the pipeline (`gleis_segmente`, `bahnhoefe`).

### 3. Set up the Python environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 4. Configure the connection

Open `config.py` and set your PostgreSQL password (the one you set during
installation), and optionally change `SEARCH_AREA` to any place name.

### 5. Run the pipeline

```bash
python load_data.py
python quality_checks.py
```

Results are printed to the terminal and saved to `output/qa_report.csv` and
`output/qa_results.gpkg` — open the `.gpkg` file in QGIS to see the flagged
issues on a map.

## Example output

Running the pipeline for Essen, Germany found:

| Check                        | Result                        |
|-------------------------------|-------------------------------|
| Track segments loaded         | 1,606                         |
| Stations loaded               | 60                             |
| Potential gaps (< 5 m)         | 1,014                          |
| Duplicate geometries           | 0                               |
| Total network length           | 313.6 km (rail), 114.9 km (tram), 12.8 km (light rail), 3.9 km (narrow gauge) |
| Stations far from any track    | 16 of 60                       |

## Possible extensions

- Change the search area in `config.py` to any other place
- Add a new check, e.g. flagging segments shorter than 5 m (likely
  digitization errors)
- Add a simple visualization script that renders the results directly with
  matplotlib, without needing QGIS

## License

This project uses OpenStreetMap data, © OpenStreetMap contributors,
available under the Open Database License (ODbL).
