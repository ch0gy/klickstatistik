import os
import datetime
import xlsxwriter
from flask import Flask
from models import db, CampusLog

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

now = datetime.datetime.now()
first_day_this_month = datetime.date(now.year, now.month, 1)
last_month = first_day_this_month - datetime.timedelta(days=1)
year = last_month.year
month = last_month.month


export_dir = r"C:\_install\Campus Statistic Tool\Gateway_PowerBI"
filename = f"CampusStatistikData.xlsx"
full_path = os.path.join(export_dir, filename)

os.makedirs(export_dir, exist_ok=True)
for file in os.listdir(export_dir):
    if file.endswith(".xlsx"):
        os.remove(os.path.join(export_dir, file))

with app.app_context():
    logs = CampusLog.query.filter(
        db.extract('year', CampusLog.timestamp) == year,
        db.extract('month', CampusLog.timestamp) == month
    ).all()

    workbook = xlsxwriter.Workbook(full_path)
    worksheet = workbook.add_worksheet()

    headers = ['Campusinfo', 'Kategorie', 'Datum']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})

    for row, log in enumerate(logs, start=1):
        if log.campusinfo and log.subject:
            worksheet.write(row, 0, log.campusinfo.name)
            worksheet.write(row, 1, log.subject.name)
            worksheet.write_datetime(row, 2, log.timestamp, date_format)

    workbook.close()