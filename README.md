# Gleistrassierung QA-Pipeline (Python + PostGIS)

Portfolio-Projekt zur Qualitätsprüfung von Bahntrassen-Geodaten.
Lädt Bahnstrecken-Daten von OpenStreetMap (Overpass API) in eine
PostGIS-Datenbank und führt automatisierte Qualitätsprüfungen durch —
genau die Art von Aufgabe, die auch bei GGO / Westnetz vorkommt,
nur hier komplett selbst gebaut und öffentlich auf GitHub zeigbar.

## Τι κάνει αυτό το project

1. Κατεβάζει δεδομένα σιδηροδρομικών γραμμών από το OpenStreetMap
   (μέσω Overpass API) για μια περιοχή της επιλογής σου (π.χ. Essen/Ruhrgebiet)
2. Τα φορτώνει σε μια τοπική βάση δεδομένων **PostGIS**
3. Τρέχει αυτόματους ελέγχους ποιότητας (quality checks):
   - Εντοπισμός "κενών" (gaps) σε τροχιές που θα έπρεπε να συνδέονται
   - Εντοπισμός διπλότυπων segments
   - Υπολογισμός συνολικού μήκους δικτύου ανά τύπο γραμμής
   - Buffer-analysis: ποιοι σταθμοί είναι πολύ κοντά σε τροχιά (< X μέτρα)
4. Εξάγει τα αποτελέσματα σε GeoPackage/CSV, έτοιμα να ανοίξεις στο QGIS

## Βήμα 1 — Εγκατάσταση εργαλείων (μία φορά)

### Windows
1. Κατέβασε και εγκατέστησε **PostgreSQL** (περιλαμβάνει και PostGIS ως extension
   στο installer): https://www.postgresql.org/download/windows/
   - Κατά την εγκατάσταση, στο "Stack Builder" που ανοίγει στο τέλος, επίλεξε
     **PostGIS** από τη λίστα spatial extensions και εγκατέστησέ το.
2. Κατέβασε **Python 3.11+**: https://www.python.org/downloads/
   (τσέκαρε το "Add Python to PATH" κατά την εγκατάσταση)

### Έλεγχος ότι όλα δουλεύουν
Άνοιξε **Command Prompt** (cmd) και τρέξε:
```
psql --version
python --version
```
Αν βλέπεις αριθμούς έκδοσης και στα δύο, είσαι έτοιμος.

## Βήμα 2 — Δημιουργία βάσης δεδομένων

Στο cmd:
```
psql -U postgres
```
(θα σου ζητήσει τον κωδικό που έβαλες κατά την εγκατάσταση)

Μέσα στο psql, τρέξε:
```sql
CREATE DATABASE gleis_qa;
\c gleis_qa
CREATE EXTENSION postgis;
\q
```

Ή απλά τρέξε το έτοιμο script που σου δίνω:
```
psql -U postgres -f setup_db.sql
```

## Βήμα 3 — Python περιβάλλον

```
python -m venv venv
venv\Scripts\activate        (Windows)
pip install -r requirements.txt
```

## Βήμα 4 — Ρύθμιση σύνδεσης

Άνοιξε το `config.py` και βάλε τον δικό σου κωδικό PostgreSQL
(τον ίδιο που έβαλες στην εγκατάσταση).

## Βήμα 5 — Τρέξε το pipeline

```
python load_data.py
python quality_checks.py
```

Τα αποτελέσματα εμφανίζονται στο τερματικό ΚΑΙ αποθηκεύονται σε
`output/qa_report.csv` και `output/qa_results.gpkg` (άνοιξέ το στο QGIS
για να δεις τα προβλήματα οπτικά, χρωματισμένα).

## Επόμενα βήματα (πρόσθεσε τα μόνος σου για να μάθεις περισσότερα)

- Άλλαξε την περιοχή αναζήτησης στο `load_data.py` (π.χ. Beelitz αντί για Essen)
- Πρόσθεσε νέο έλεγχο: γραμμές με μήκος < 5 μέτρα (πιθανό σφάλμα ψηφιοποίησης)
- Ανέβασέ το στο GitHub με screenshots από το QGIS στο README

## GitHub

Όταν είναι έτοιμο:
```
git init
git add .
git commit -m "Initial commit: Gleis QA pipeline"
```
Δημιούργησε repo στο github.com και κάνε push. Βάλε link στο LinkedIn/CV.
