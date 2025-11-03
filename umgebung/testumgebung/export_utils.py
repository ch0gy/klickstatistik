"""Utilities for exporting campus logs to Excel and uploading them to SharePoint."""
from __future__ import annotations

import datetime as _dt
import os
from typing import List, Optional, Sequence, Tuple

import xlsxwriter
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

from models import CampusLog, db

HEADERS: Sequence[str] = ("Campusinfo", "Kategorie", "Datum")


def get_previous_month(reference: Optional[_dt.date] = None) -> Tuple[int, int]:
    """Return the (year, month) tuple for the month prior to *reference*."""
    reference = reference or _dt.date.today()
    first_day_this_month = _dt.date(reference.year, reference.month, 1)
    last_day_previous_month = first_day_this_month - _dt.timedelta(days=1)
    return last_day_previous_month.year, last_day_previous_month.month


def _resolve_export_directory(directory: Optional[str]) -> str:
    directory = directory or os.environ.get("EXPORT_DIRECTORY") or os.getcwd()
    return directory


def _resolve_filename(filename: Optional[str]) -> str:
    return filename or os.environ.get("EXPORT_FILENAME") or "CampusStatistikData.xlsx"


def fetch_logs(year: int, month: int, campus_id: Optional[int] = None) -> List[CampusLog]:
    """Retrieve campus logs for the provided year/month combination."""
    query = CampusLog.query.filter(
        db.extract("year", CampusLog.timestamp) == year,
        db.extract("month", CampusLog.timestamp) == month,
    )
    if campus_id:
        query = query.filter(CampusLog.campusinfo_id == campus_id)
    return query.all()


def _rows_from_logs(logs: Sequence[CampusLog]) -> List[Tuple[str, str, _dt.datetime]]:
    rows: List[Tuple[str, str, _dt.datetime]] = []
    for log in logs:
        if log.campusinfo and log.subject:
            rows.append((log.campusinfo.name, log.subject.name, log.timestamp))
    return rows


def export_logs_to_excel(
    year: int,
    month: int,
    *,
    campus_id: Optional[int] = None,
    directory: Optional[str] = None,
    filename: Optional[str] = None,
    cleanup: bool = False,
) -> Tuple[str, List[Tuple[str, str, _dt.datetime]]]:
    """Create an Excel export for the given month and return the file path and rows."""
    export_dir = _resolve_export_directory(directory)
    os.makedirs(export_dir, exist_ok=True)
    target_filename = _resolve_filename(filename)
    full_path = os.path.join(export_dir, target_filename)

    if cleanup:
        for existing in os.listdir(export_dir):
            if existing.endswith(".xlsx") and existing != target_filename:
                try:
                    os.remove(os.path.join(export_dir, existing))
                except OSError:
                    pass

    logs = fetch_logs(year, month, campus_id)
    rows = _rows_from_logs(logs)

    workbook = xlsxwriter.Workbook(full_path)
    worksheet = workbook.add_worksheet()
    header_format = workbook.add_format({"bold": True})
    date_format = workbook.add_format({"num_format": "dd.mm.yyyy hh:mm"})

    for column, header in enumerate(HEADERS):
        worksheet.write(0, column, header, header_format)

    for row_index, (campus_name, subject_name, timestamp) in enumerate(rows, start=1):
        worksheet.write(row_index, 0, campus_name)
        worksheet.write(row_index, 1, subject_name)
        worksheet.write_datetime(row_index, 2, timestamp, date_format)

    for column in range(len(HEADERS)):
        values = [len(str(HEADERS[column]))]
        if column == 2:
            values.extend(len(ts.strftime("%d.%m.%Y %H:%M")) for *_, ts in rows)
        else:
            values.extend(len(str(row[column])) for row in rows)
        worksheet.set_column(column, column, max(values) if values else 10)

    workbook.close()
    return full_path, rows


def _build_sharepoint_credentials():
    client_id = os.environ.get("SHAREPOINT_CLIENT_ID")
    client_secret = os.environ.get("SHAREPOINT_CLIENT_SECRET")
    username = os.environ.get("SHAREPOINT_USERNAME")
    password = os.environ.get("SHAREPOINT_PASSWORD")

    if client_id and client_secret:
        return ClientCredential(client_id, client_secret)
    if username and password:
        return UserCredential(username, password)
    raise ValueError("SharePoint credentials are not configured.")


def _normalize_sharepoint_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return normalized


def upload_file_to_sharepoint(local_path: str, target_filename: Optional[str] = None) -> str:
    """Upload *local_path* to SharePoint and return the server-relative URL."""
    site_url = os.environ.get("SHAREPOINT_SITE_URL")
    target_path = os.environ.get("SHAREPOINT_TARGET_PATH")

    if not site_url or not target_path:
        raise ValueError("SharePoint site configuration is incomplete.")

    credentials = _build_sharepoint_credentials()
    ctx = ClientContext(site_url).with_credentials(credentials)
    folder = ctx.web.get_folder_by_server_relative_url(_normalize_sharepoint_path(target_path))

    name = target_filename or os.path.basename(local_path)
    with open(local_path, "rb") as file_handle:
        content = file_handle.read()
    uploaded_file = folder.upload_file(name, content, overwrite=True)
    ctx.execute_query()
    return uploaded_file.serverRelativeUrl
