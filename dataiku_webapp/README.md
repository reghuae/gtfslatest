# Dataiku GTFS Downloader Webapp

A minimal Dataiku **Standard webapp** that lets you click-and-download the GTFS
files stored in the `pta_wojhati_raw` Hive database (tables
`wojhati_gtfs_stops`, `wojhati_gtfs_routes`, `wojhati_gtfs_trips`,
`wojhati_gtfs_stop_times`, …), either one file at a time (as `stops.txt`,
`routes.txt`, etc.) or all together as a single `gtfs.zip`.

## Setup (5 minutes)

1. In your Dataiku project (e.g. **RTABUSSCN**) go to
   **</> (Code) → Webapps → + New webapp → Code webapp → Standard**.
   Pick "An empty Standard webapp" and give it a name (e.g. *GTFS Downloader*).
2. Copy the four files of this folder into the matching tabs of the webapp
   editor:
   - `body.html`  → **HTML** tab
   - `script.js`  → **JS** tab
   - `style.css`  → **CSS** tab
   - `backend.py` → **Python** tab
3. In the **Python** tab, set the config at the top of `backend.py`:
   - `HIVE_CONNECTION` — the name of the Hive connection your project uses
     (the connection you selected in the *New Hive dataset* screen).
   - `HIVE_DATABASE` (default `pta_wojhati_raw`) and `TABLE_PREFIX`
     (default `wojhati_gtfs_`) normally need no change.
4. In **Settings** of the webapp, enable the **Python backend**
   ("Backend: Enabled") and start it.
5. Open the webapp: you get a table of the 12 GTFS files with a
   **Download** button each, plus **Download all as gtfs.zip**.

## Notes

- If your project already contains Dataiku datasets imported from those Hive
  tables (same names, e.g. `wojhati_gtfs_stops`), the backend reads the
  dataset directly; otherwise it queries Hive through `HIVE_CONNECTION` with
  `SELECT * FROM pta_wojhati_raw.<table>`.
- `calendar` / `calendar_dates` are listed as optional: if the tables do not
  exist in the database, the single-file download shows an error for them and
  the zip download simply records them as skipped in `_download_report.txt`.
- `stop_times` and `shapes` are the big ones — the export can take a couple of
  minutes and needs enough memory on the backend; if the backend is
  memory-limited, raise it in the webapp settings (Backend → container /
  memory) or download those two files individually.
- The backend needs a code environment with `pandas` (the Dataiku builtin
  environment is fine).

## Purpose

The downloaded files feed the *illegal parking at bus stops → On-Time
Performance impact* study (see `../STUDY_NOTES.md`): `stop_times.txt` +
`trips.txt` + `calendar.txt` give scheduled buses per stop in the peak hours,
`stops.txt` locates the affected stops, and `routes.txt` maps the affected
routes (10, 13A, C01, 61, …).
