# -*- coding: utf-8 -*-
"""
Dataiku Standard Webapp - Python backend
GTFS file downloader for the pta_wojhati_raw Hive database.

Paste this into the "Python" tab of a Dataiku Standard webapp.

How it resolves data, per GTFS table:
  1. If the project contains a Dataiku dataset named exactly like the Hive
     table (e.g. "wojhati_gtfs_stops"), it reads that dataset.
  2. Otherwise it runs "SELECT * FROM pta_wojhati_raw.<table>" through the
     Hive connection configured below (SQLExecutor2).

=> You only have to set HIVE_CONNECTION to the name of the Hive connection
   used in your project (the one shown in the "New Hive dataset" screen).
"""

import io
import tempfile
import traceback
import zipfile

import dataiku
from flask import Response, jsonify, send_file

# --------------------------------------------------------------------------
# CONFIG - adjust these three values if needed
# --------------------------------------------------------------------------
HIVE_CONNECTION = "hiveserver2"        # <-- Dataiku Hive connection name
HIVE_DATABASE = "pta_wojhati_raw"      # Hive database holding the GTFS tables
TABLE_PREFIX = "wojhati_gtfs_"         # table name prefix in the database

# GTFS files exposed for download. "required" only affects UI labelling.
# calendar / calendar_dates are included in case they exist in the database
# even though they were not visible in the table list screenshot.
GTFS_FILES = [
    {"name": "stops",          "required": True},
    {"name": "routes",         "required": True},
    {"name": "trips",          "required": True},
    {"name": "stop_times",     "required": True},
    {"name": "calendar",       "required": False},
    {"name": "calendar_dates", "required": False},
    {"name": "frequencies",    "required": False},
    {"name": "shapes",         "required": False},
    {"name": "transfers",      "required": False},
    {"name": "pathways",       "required": False},
    {"name": "levels",         "required": False},
    {"name": "feed_info",      "required": False},
]

_VALID_NAMES = {f["name"] for f in GTFS_FILES}


# --------------------------------------------------------------------------
# Data access helpers
# --------------------------------------------------------------------------
def _dataset_exists(dataset_name):
    """True if a Dataiku dataset with this name exists in the project."""
    try:
        dataiku.Dataset(dataset_name).get_config()
        return True
    except Exception:
        return False


def _read_table_df(gtfs_name):
    """Return a pandas DataFrame for one GTFS table.

    Prefers a project dataset named like the Hive table, falls back to a
    direct Hive query through HIVE_CONNECTION.
    """
    table = TABLE_PREFIX + gtfs_name
    if _dataset_exists(table):
        return dataiku.Dataset(table).get_dataframe(infer_with_pandas=False)

    from dataiku.core.sql import SQLExecutor2
    executor = SQLExecutor2(connection=HIVE_CONNECTION)
    query = "SELECT * FROM {}.{}".format(HIVE_DATABASE, table)
    return executor.query_to_df(query)


def _df_to_gtfs_csv(df):
    """Serialize a DataFrame to GTFS-style CSV (UTF-8, no index)."""
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    return buf.getvalue().encode("utf-8")


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/tables")  # noqa: F821 - `app` is provided by Dataiku
def list_tables():
    """List the GTFS files offered for download, with availability info."""
    out = []
    for f in GTFS_FILES:
        table = TABLE_PREFIX + f["name"]
        out.append({
            "name": f["name"],
            "filename": f["name"] + ".txt",
            "table": "{}.{}".format(HIVE_DATABASE, table),
            "required": f["required"],
            "as_dataset": _dataset_exists(table),
        })
    return jsonify({"connection": HIVE_CONNECTION, "files": out})


@app.route("/download/<gtfs_name>")  # noqa: F821
def download_one(gtfs_name):
    """Download a single GTFS table as <name>.txt (CSV)."""
    if gtfs_name not in _VALID_NAMES:
        return Response("Unknown GTFS file: %s" % gtfs_name, status=404)
    try:
        payload = _df_to_gtfs_csv(_read_table_df(gtfs_name))
    except Exception:
        return Response(
            "Failed to read %s:\n%s" % (gtfs_name, traceback.format_exc()),
            status=500, mimetype="text/plain")
    return Response(
        payload,
        mimetype="text/csv",
        headers={"Content-Disposition":
                 "attachment; filename=%s.txt" % gtfs_name})


@app.route("/download_all")  # noqa: F821
def download_all():
    """Download every available GTFS table bundled as gtfs.zip.

    Tables that fail to read (e.g. missing calendar) are skipped and listed
    in _download_report.txt inside the zip instead of failing the download.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    report_lines = []
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in GTFS_FILES:
                name = f["name"]
                try:
                    zf.writestr(name + ".txt",
                                _df_to_gtfs_csv(_read_table_df(name)))
                    report_lines.append("OK      %s.txt" % name)
                except Exception as exc:
                    report_lines.append("SKIPPED %s.txt -> %s" % (name, exc))
            zf.writestr("_download_report.txt", "\n".join(report_lines))
        tmp.close()
        return send_file(tmp.name, as_attachment=True,
                         download_name="gtfs.zip", mimetype="application/zip")
    finally:
        # send_file streams from disk, so the temp file cannot be deleted
        # here; the backend's temp dir is cleaned up by the OS/instance.
        if not tmp.closed:
            tmp.close()
