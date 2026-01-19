# Klickstatistik (Campus Statistik Tool)

## Überblick
Das Campus Statistik Tool ist eine Flask-Webanwendung zum Erfassen von Klickstatistiken pro Campus und Thema sowie zum Export dieser Logs nach Excel oder direkt zu SharePoint. Es gibt einen Admin-Bereich zur Verwaltung von Campuses, Themen und Accounts sowie eine Oberfläche zum Erfassen der Klicks. Der Export kann als Download im Browser erfolgen oder serverseitig zu SharePoint hochgeladen werden. Zusätzlich liegt ein Skript für den monatlichen Export bei.

## Repository-Struktur
- `umgebung/testumgebung/main.py`: Einstiegspunkt der Flask-App, Konfiguration und UI-Routen für die Campus-Ansicht. Initialisiert die Datenbank und legt ein Admin-Konto an, falls es noch nicht existiert.
- `umgebung/testumgebung/admin.py`: Admin- und Data-Blueprints, Login/Logout, Verwaltung von Campuses/Themen/Accounts, Log-Erfassung sowie Export-Endpunkte.
- `umgebung/testumgebung/models.py`: SQLAlchemy-Modelle für Campus, Thema, Log und Account.
- `umgebung/testumgebung/export_utils.py`: Export-Hilfsfunktionen für Excel und SharePoint-Upload.
- `umgebung/testumgebung/update-file.py`: Standalone-Skript für den Export des Vormonats inkl. SharePoint-Upload.
- `umgebung/testumgebung/templates/` und `umgebung/testumgebung/static/`: HTML-Templates und statische Assets.

## Ablauf der Anwendung
1. **Flask-App starten**
   - `main.py` richtet Flask, SQLAlchemy und den Login-Manager ein.
   - Die SQLite-Datenbank (`database.db`) wird erstellt und ein `admin`-Account angelegt, falls nötig.
   - Die Blueprints `admin` und `data` werden registriert.

2. **Login & Nutzung**
   - Der Login erfolgt über `/login` (Data-Blueprint). Für die Nutzung ist eine Anmeldung erforderlich.
   - `/` listet Campuses, `/campuses/<name>` zeigt die Themen des gewählten Campus.
   - Ein Klick auf ein Thema erstellt einen Eintrag über `/log/<campusid>/<subjectid>` in `CampusLog`.

3. **Admin-Verwaltung**
   - `/admin` zeigt das Admin-Dashboard.
   - Campuses, Themen und Accounts werden über `/admin/campuses`, `/admin/subjects` und `/admin/accounts` verwaltet.

4. **Export**
   - `/export` erzeugt einen Excel-Download.
   - `/export/sharepoint` erzeugt die Datei und lädt sie auf SharePoint hoch.

## Datenmodell
- **CampusInfo**: enthält Campusnamen.
- **Subject**: enthält Themenname, Farbe und optionales Piktogramm.
- **CampusSubject**: Zuordnungstabelle zwischen Campuses und Themen (Many-to-Many).
- **CampusLog**: protokolliert Klicks (Campus, Thema, Zeitstempel).
- **Account**: Login-Daten für Mitarbeitende.

## Export Utilities (`export_utils.py`)
Der Export besteht aus zwei Teilen: Excel-Datei erzeugen und optional zu SharePoint hochladen.

### 1. Excel-Datei erzeugen
`export_logs_to_excel(year, month, campus_id=None, directory=None, filename=None, cleanup=False)`

**Ablauf im Detail:**
1. **Export-Verzeichnis bestimmen**
   - Verwendet das Argument `directory`, falls angegeben.
   - Sonst `EXPORT_DIRECTORY` aus der Umgebung.
   - Default: aktuelles Arbeitsverzeichnis.

2. **Dateiname bestimmen**
   - Verwendet das Argument `filename`, falls angegeben.
   - Sonst `EXPORT_FILENAME` aus der Umgebung.
   - Default: `CampusStatistikData.xlsx`.

3. **Optionales Aufräumen**
   - Bei `cleanup=True` werden bestehende `.xlsx`-Dateien im Export-Verzeichnis gelöscht, **außer** der aktuellen Zieldatei.

4. **Logs laden**
   - `fetch_logs(year, month, campus_id)` filtert `CampusLog` nach Jahr/Monat.
   - Falls `campus_id` gesetzt ist, wird zusätzlich darauf gefiltert.

5. **Zeilen für Excel bauen**
   - `_rows_from_logs` erzeugt Tupel `(campus_name, subject_name, timestamp)`.
   - Logs ohne Campus- oder Subject-Beziehung werden übersprungen.

6. **Workbook schreiben**
   - Die Funktion schreibt die Header `Campusinfo`, `Kategorie`, `Datum` und alle Log-Zeilen.
   - Das Datumsformat lautet `dd.mm.yyyy hh:mm`.
   - Spaltenbreiten werden anhand des Inhalts angepasst.

7. **Rückgabewerte**
   - Gibt `(full_path, rows)` zurück: Dateipfad und Log-Daten.

### 2. Upload nach SharePoint
`upload_file_to_sharepoint(local_path, target_filename=None)`

**So funktioniert der Upload:**
1. **Konfiguration laden**
   - `SHAREPOINT_SITE_URL`: SharePoint-Site-URL.
   - `SHAREPOINT_TARGET_PATH`: server-relativer Zielordner.
   - Fehlende Werte führen zu `ValueError`.

2. **Credentials erstellen**
   - `_build_sharepoint_credentials()` nutzt:
     - `SHAREPOINT_CLIENT_ID`
     - `SHAREPOINT_CLIENT_SECRET`
   - Fehlende Werte führen zu `ValueError`.
   - Es wird App-Only-Auth mit Client-Credentials genutzt; Username/Passwort-Login ist nicht unterstützt.

3. **Pfad normalisieren**
   - `_normalize_sharepoint_path()` ersetzt Backslashes und stellt ein führendes `/` sicher.

4. **Datei hochladen**
   - Die Datei wird aus `local_path` gelesen.
   - Upload erfolgt in den Zielordner mit `ClientContext`.
   - Rückgabe: server-relativer URL der hochgeladenen Datei.

### 3. Auslöser im System
- **Admin-Route (`/export/sharepoint`)**
  - Erzeugt eine Excel-Datei im Temp-Verzeichnis.
  - Lädt diese mit `upload_file_to_sharepoint()` hoch.
  - Zeigt Erfolg/Fehler als Flash-Message.

- **Standalone-Skript (`update-file.py`)**
  - Berechnet den Vormonat mit `get_previous_month()`.
  - Erzeugt die Excel-Datei (optional Cleanup).
  - Lädt die Datei nach SharePoint hoch.
  - Schreibt Statusmeldungen ins Terminal (für Cron/Task Scheduler geeignet).

## Umgebungsvariablen
Die folgenden Variablen werden im Code referenziert und sollten (z. B. via `.env`) gesetzt werden:

### Kern-Anwendung
- `SECRET_KEY`: Flask Secret Key.
- `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_NAME`: in `main.py` vorhanden (aktuell SQLite genutzt).

### Export-Konfiguration
- `EXPORT_DIRECTORY`: optionales Export-Verzeichnis.
- `EXPORT_FILENAME`: optionaler Dateiname.

### SharePoint-Upload
- `SHAREPOINT_SITE_URL`: SharePoint Site-URL.
- `SHAREPOINT_TARGET_PATH`: server-relativer Zielordner.
- `SHAREPOINT_CLIENT_ID`: SharePoint App Client ID.
- `SHAREPOINT_CLIENT_SECRET`: SharePoint App Secret.

## Lokales Ausführen
1. Virtuelle Python-Umgebung erstellen und aktivieren.
2. Abhängigkeiten aus `requirements.txt` installieren.
3. `SECRET_KEY` und ggf. SharePoint-Variablen setzen.
4. Anwendung starten:
   ```bash
   python umgebung/testumgebung/main.py
   ```
   Standardmäßig läuft die App auf `127.0.0.1:3306` im Debug-Modus.

## Geplanter SharePoint-Export
Monatlichen Export starten:
```bash
python umgebung/testumgebung/update-file.py
```
Das Skript exportiert den **Vormonat** und lädt die Datei auf SharePoint hoch.

## Hinweise
- Die Anwendung nutzt SQLite (`database.db`) wie in `main.py` konfiguriert.
- Bei Deployment in anderen Umgebungen Datenbank- und SharePoint-Zugangsdaten anpassen.
- IDE-Metadaten und Python-Cache-Verzeichnisse (z. B. `.idea/`, `__pycache__/`) sollten nicht eingecheckt werden.
