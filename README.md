# Gleis QA Pipeline (Python + PostGIS)

**[English](#english) | [Deutsch](#deutsch)**

---

## English

A portfolio project for quality-checking railway geodata. Downloads railway
track and station data from OpenStreetMap (Overpass API), loads it into a
PostGIS database, and runs automated data-quality checks — the same kind of
task performed professionally in railway surveying and utility geodata
management, built here end-to-end as a personal project.

### What this project does

1. Downloads railway line and station data from OpenStreetMap for an area of
   your choice (e.g. Essen, Germany)
2. Loads the data into a local **PostGIS** database
3. Runs automated quality checks:
   - Gap detection: track segments that should connect but don't
   - Duplicate detection: (near-)identical line geometries
   - Total network length by railway type
   - Buffer analysis: stations that are unexpectedly far from any track
4. Exports the results as a GeoPackage/CSV, ready to open in QGIS

### Tech stack

- **Python** (geopandas, osmnx, SQLAlchemy, psycopg2)
- **PostgreSQL / PostGIS** for spatial data storage and SQL-based analysis
- **QGIS** for visualizing the results

### Setup

**1. Install prerequisites (one-time)**

- **PostgreSQL** (includes PostGIS via the Stack Builder during installation):
  https://www.postgresql.org/download/
- **Python 3.11+**: https://www.python.org/downloads/

**2. Create the database**

```bash
psql -U postgres -f setup_db.sql
```

This creates the `gleis_qa` database, enables the PostGIS extension, and
creates the two tables used by the pipeline (`gleis_segmente`, `bahnhoefe`).

**3. Set up the Python environment**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

**4. Configure the connection**

Open `config.py` and set your PostgreSQL password (the one you set during
installation), and optionally change `SEARCH_AREA` to any place name.

**5. Run the pipeline**

```bash
python load_data.py
python quality_checks.py
```

Results are printed to the terminal and saved to `output/qa_report.csv` and
`output/qa_results.gpkg` — open the `.gpkg` file in QGIS to see the flagged
issues on a map.

### Example output

Running the pipeline for Essen, Germany found:

| Check                        | Result                        |
|-------------------------------|-------------------------------|
| Track segments loaded         | 1,606                         |
| Stations loaded               | 60                             |
| Potential gaps (< 5 m)         | 1,014                          |
| Duplicate geometries           | 0                               |
| Total network length           | 313.6 km (rail), 114.9 km (tram), 12.8 km (light rail), 3.9 km (narrow gauge) |
| Stations far from any track    | 16 of 60                       |

### Possible extensions

- Change the search area in `config.py` to any other place
- Add a new check, e.g. flagging segments shorter than 5 m (likely
  digitization errors)
- Add a simple visualization script that renders the results directly with
  matplotlib, without needing QGIS

### License

This project uses OpenStreetMap data, © OpenStreetMap contributors,
available under the Open Database License (ODbL).

---

## Deutsch

Ein Portfolio-Projekt zur Qualitätsprüfung von Bahntrassen-Geodaten. Lädt
Bahnstrecken- und Bahnhofsdaten von OpenStreetMap (Overpass API) in eine
PostGIS-Datenbank und führt automatisierte Datenqualitätsprüfungen durch —
genau die Art von Aufgabe, die auch in der Bahnvermessung und im
Netzinformationsmanagement vorkommt, hier komplett selbst gebaut als
persönliches Projekt.

### Was dieses Projekt macht

1. Lädt Bahnstrecken- und Bahnhofsdaten von OpenStreetMap für ein Gebiet
   deiner Wahl (z. B. Essen, Deutschland)
2. Speichert die Daten in einer lokalen **PostGIS**-Datenbank
3. Führt automatisierte Qualitätsprüfungen durch:
   - Lückenerkennung: Gleissegmente, die verbunden sein sollten, es aber
     nicht sind
   - Duplikaterkennung: (nahezu) identische Liniengeometrien
   - Gesamtstreckenlänge je Bahntyp
   - Buffer-Analyse: Bahnhöfe, die auffällig weit von jeder Strecke entfernt
     liegen
4. Exportiert die Ergebnisse als GeoPackage/CSV, direkt einsatzbereit in QGIS

### Technologien

- **Python** (geopandas, osmnx, SQLAlchemy, psycopg2)
- **PostgreSQL / PostGIS** für räumliche Datenhaltung und SQL-basierte Analyse
- **QGIS** zur Visualisierung der Ergebnisse

### Einrichtung

**1. Voraussetzungen installieren (einmalig)**

- **PostgreSQL** (inkl. PostGIS über den Stack Builder während der
  Installation): https://www.postgresql.org/download/
- **Python 3.11+**: https://www.python.org/downloads/

**2. Datenbank erstellen**

```bash
psql -U postgres -f setup_db.sql
```

Dies erstellt die Datenbank `gleis_qa`, aktiviert die PostGIS-Erweiterung und
legt die zwei Tabellen an, die die Pipeline nutzt (`gleis_segmente`,
`bahnhoefe`).

**3. Python-Umgebung einrichten**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

**4. Verbindung konfigurieren**

Öffne `config.py` und trage dein PostgreSQL-Passwort ein (dasselbe, das du
bei der Installation gesetzt hast), und ändere optional `SEARCH_AREA` auf ein
beliebiges Gebiet.

**5. Pipeline ausführen**

```bash
python load_data.py
python quality_checks.py
```

Die Ergebnisse werden im Terminal ausgegeben und in `output/qa_report.csv`
sowie `output/qa_results.gpkg` gespeichert — öffne die `.gpkg`-Datei in QGIS,
um die erkannten Probleme auf der Karte zu sehen.

### Beispielergebnis

Ein Durchlauf für Essen, Deutschland ergab:

| Prüfung                        | Ergebnis                      |
|----------------------------------|-------------------------------|
| Geladene Gleissegmente            | 1.606                          |
| Geladene Bahnhöfe                 | 60                              |
| Potenzielle Lücken (< 5 m)         | 1.014                           |
| Doppelte Geometrien                | 0                                |
| Gesamtstreckenlänge                | 313,6 km (Rail), 114,9 km (Tram), 12,8 km (Light Rail), 3,9 km (Narrow Gauge) |
| Bahnhöfe weit von jeder Strecke    | 16 von 60                       |

### Mögliche Erweiterungen

- Suchgebiet in `config.py` auf ein beliebiges anderes Gebiet ändern
- Neue Prüfung hinzufügen, z. B. Markierung von Segmenten unter 5 m Länge
  (wahrscheinliche Digitalisierungsfehler)
- Ein einfaches Visualisierungsskript hinzufügen, das die Ergebnisse direkt
  mit matplotlib darstellt, ohne QGIS zu benötigen

### Lizenz

Dieses Projekt verwendet OpenStreetMap-Daten, © OpenStreetMap-Mitwirkende,
verfügbar unter der Open Database License (ODbL).
