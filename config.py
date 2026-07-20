"""
Datenbank-Verbindungseinstellungen.
Passe hier dein PostgreSQL-Passwort an (dasselbe, das du bei der Installation gesetzt hast).
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "gleis_qa",
    "user": "postgres",
    "password": "Falagas19942008!",  # <-- hier dein PostgreSQL-Passwort eintragen
}

SQLALCHEMY_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

# Suchgebiet für OSM-Daten (Overpass API).
# Ändere dies auf ein Gebiet deiner Wahl, z. B. "Beelitz, Germany" oder "Essen, Germany".
SEARCH_AREA = "Essen, Germany"

# Maximaler Abstand (Meter), ab dem eine Lücke zwischen zwei Gleissegmenten
# als potenzielles Datenproblem markiert wird.
GAP_THRESHOLD_METERS = 5.0

# Maximaler Abstand (Meter) für die Bahnhof-Nähe-Prüfung.
STATION_BUFFER_METERS = 50.0
