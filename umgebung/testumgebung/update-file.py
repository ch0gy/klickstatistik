import os
from flask import Flask
from models import db
from export_utils import export_logs_to_excel, upload_file_to_sharepoint, get_previous_month

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


year, month = get_previous_month()

export_dir = os.environ.get(
    'EXPORT_DIRECTORY',
    r"C:\_install\Campus Statistic Tool\Gateway_PowerBI",
)
filename = os.environ.get('EXPORT_FILENAME', 'CampusStatistikData.xlsx')

with app.app_context():
    file_path, _ = export_logs_to_excel(
        year,
        month,
        directory=export_dir,
        filename=filename,
        cleanup=True,
    )

    try:
        upload_file_to_sharepoint(file_path, target_filename=filename)
        print('Upload nach SharePoint abgeschlossen.')
    except ValueError as exc:
        print(f'SharePoint Upload übersprungen: {exc}')
    except Exception as exc:  # pylint: disable=broad-except
        print(f'Fehler beim Hochladen nach SharePoint: {exc}')
