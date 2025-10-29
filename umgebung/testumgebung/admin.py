import xlsxwriter
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash, make_response
from flask_login import login_user, logout_user, login_required
from passlib.hash import sha256_crypt
import datetime
from models import db, CampusInfo, Subject, CampusSubject, CampusLog, Account

app = Flask(__name__)

admin_blueprint = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')
data_blueprint = Blueprint('data', __name__, template_folder='templates')

@data_blueprint.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        rememberme = False 
        user = Account.query.filter_by(username = username).first()
        if user:
            if not sha256_crypt.verify(password, user.password):
                flash("Falsche Login-Daten.", "danger")
            else:
                if len(request.form.getlist("remembermebox")) == 1:
                    rememberme = True
                login_user(user, remember=rememberme)
                next = request.args.get('next')
                flash("Anmeldung war erfolgreich.", "success")
                return redirect(next or url_for('index'))
        else:
            flash("Falsche Login-Daten.", "danger")
        return render_template('/admin/login.html')
    else:
        return render_template('/admin/login.html')
    
@data_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@admin_blueprint.route('/')
@login_required
def admin():
    data = []
    account_data = Account.query.all()
    campuses = CampusInfo.query.all()
    subjects = Subject.query.all()
    campus_logs = CampusLog.query.order_by(CampusLog.id.desc()).limit(15).all()
    
    for campus in campuses:
        campussubjects = CampusSubject.query.where(CampusSubject.campusinfo_id == campus.id).all()
        campussubjectslist = []
        for campussubject in campussubjects:
            campussubjectslist.append(Subject.query.where(Subject.id == campussubject.subject_id).first())
        campus.subjects = campussubjectslist
        campus.unused_subjects = [subject for subject in subjects if subject not in campus.subjects]
    return render_template('/admin/admin.html', account_data=account_data, campuses=campuses, subjects=subjects, dataset=campus_logs, data=data, datetime=datetime)

@data_blueprint.route('/log/<campusid>/<subjectid>')
@login_required
def data_log(campusid, subjectid):
    try:
        campus = CampusInfo.query.filter_by(id=campusid).first()
        subject = Subject.query.filter_by(id=subjectid).first()
        campuslog = CampusLog(campusinfo_id=campus.id, subject_id=subject.id, timestamp=datetime.datetime.now())
        db.session.add(campuslog)
        db.session.commit()
    except: 
        flash("Anfrage war nicht erfolgreich.", "danger")
    else:
        flash("Eintrag erfolgreich hinzugefügt.", "success")
    return redirect("/campuses/%s"%(campus.name.replace(' ', '-').lower()))

@data_blueprint.route("/export", methods=['GET', 'POST'])
@login_required
def export():
    if request.method == 'POST':
        year = int(request.form.get('year-export-filter'))
        month = int(request.form.get('month-export-filter'))
        campus = int(request.form.get('campus-export-filter'))

        if campus == 0:
            campus = None
        return redirect(url_for('data.export', year=year, month=month, campus=campus))
    elif request.method == 'GET':
        # Set year and month to current year and month
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        # Get year and month from request
        if (request.args.get('year')):
            year = request.args.get('year')
        if (request.args.get('month')):
            month = request.args.get('month')

        # Set custom headers
        headers = ['Campusinfo', 'Kategorie', 'Datum']

        # Query the database and store the results in a list of tuples
        query = CampusLog.query.filter(
            db.extract('year', CampusLog.timestamp) == year,
            db.extract('month', CampusLog.timestamp) == month,
        )

        if (request.args.get('campus')):
            query = query.filter(CampusLog.campusinfo_id == request.args.get('campus'))
        campuslogs = query.all()

        data = [(cl.campusinfo.name, cl.subject.name, cl.timestamp) for cl in campuslogs if cl.campusinfo and cl.subject]

        # Create a new workbook and add a worksheet
        workbook = xlsxwriter.Workbook('CampusStatistikData.xlsx')
        worksheet = workbook.add_worksheet()
        bold_format = workbook.add_format({'bold': True})

        # Write the headers to the first row
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, bold_format)

        # Write the data to subsequent rows
        date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm:ss'})
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                if col == 2:
                    worksheet.write(row + 1, col, cell_data, date_format)
                else:
                    worksheet.write(row + 1, col, cell_data)

        for col, header in enumerate(headers):
            max_width = max([len(str(header))] + [len(str(row_data[col])) for row_data in data])
            worksheet.set_column(col, col, max_width)
            
        # Close the workbook
        workbook.close()

        # Return the Excel file as a Flask response
        with open('CampusStatistikData.xlsx', mode='rb') as file:
            response = make_response(file.read())

        response.headers['Content-Disposition'] = 'attachment; filename=CampusStatistikData.xlsx'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return response

@admin_blueprint.route('/accounts', methods=['POST'])
@login_required
def accounts():
    if request.method == 'POST':
        # Abrufen der Werte aus dem Formular
        username = request.form.get('add_username')
        firstname = request.form.get('add_firstname')
        surname = request.form.get('add_surname')
        password = request.form.get('add_password')
        # Hinzufügen der Werte in die Datenbank
        account = Account(username=username, firstname=firstname, surname=surname, password=sha256_crypt.hash(password))
        db.session.add(account)
        db.session.commit()
        # return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

@admin_blueprint.route('/accounts/<method>/<username>', methods=["POST"])
@login_required
def update_account(method, username):
    if method.lower() == 'delete':
        # Löschen der Werte aus der Datenbank
        acounts = Account.query.all()
        if len(acounts) <= 1:
            flash("You can't delete the last account.", "danger")
            return redirect(url_for('admin.admin', tab='account'))
        account = Account.query.filter_by(username=username).first()
        db.session.delete(account)
        db.session.commit()
        # Umleitung zur Seite mit der aktualisierten Tabelle
        return redirect(url_for('admin.admin'))
    elif method == 'put':
        # Abrufen der Werte aus dem Formular
        new_username = request.form.get('username')
        new_firstname = request.form.get('firstname')
        new_surname = request.form.get('surname')
        new_password = request.form.get('password')
        # Aktualisieren der Werte in der Datenbank
        account = Account.query.filter_by(username=username).first()
        account.username = new_username
        account.firstname = new_firstname
        account.surname = new_surname
        if (new_password): 
            account.password = sha256_crypt.hash(new_password)
        db.session.commit()
        # return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

@admin_blueprint.route('/campuses', methods=['POST'])
@login_required
def campuses():
    if request.method == "POST":
        # Abrufen der Werte aus dem Formular
        campusname = request.form.get('add_campusname')
        subjects = request.form.getlist('add_subjects')

        existing_campus = CampusInfo.query.filter_by(name=campusname).first()
        if existing_campus:
            flash('Campusname existiert bereits.', 'danger')
            return redirect(url_for('admin.admin', tab='campus'))

        campus = CampusInfo(name=campusname)
        db.session.add(campus)
        db.session.commit()

        for subject in subjects:
            campussubject = CampusSubject(campusinfo_id=campus.id, subject_id=subject)
            db.session.add(campussubject)
            db.session.commit()
        # Hinzufügen der Werte in die Datenbank

        # Upload image
        # campusinfoname = campusname.lower()
        # campusinfoname = campusinfoname.replace(' ', '-')
        image = request.files['add_campusimage']

        if image:
            filename = secure_filename(image.filename)
            filename = str(campus.id) + '.' + filename.rsplit('.', 1)[1].lower()
            image.save(os.path.join('static/images/campuses', filename))
            campus.image = filename

        db.session.commit()
    return redirect(url_for('admin.admin', tab='campus'))



@admin_blueprint.route('/campuses/<method>/<campusid>', methods=["POST"])
@login_required
def update_campus(method, campusid):
    imagepath = 'static/images/campuses'
    print(method)
    if method.lower() == "delete":
        campus = CampusInfo.query.filter_by(id=campusid).first()
        campus_subjects = CampusSubject.query.filter_by(campusinfo_id=campusid).all()
        for campus_subject in campus_subjects:
            db.session.delete(campus_subject)
            db.session.commit()
        db.session.delete(campus)
        db.session.commit()

        # Delete image
        # campusinfoname = campus.name.lower()
        # campusinfoname = campusinfoname.replace(' ', '-')
        path = os.path.join(imagepath, secure_filename(str(campus.id) + '.jpg'))
        if os.path.exists(path):
            os.remove(path)
    elif method.lower() == "put":
        campusname = request.form.get('campusname')
        image = request.files['campusimage']

        # existing_campus = CampusInfo.query.filter_by(name=campusname).first()
        # if existing_campus:
        #     flash('Campusname existiert bereits.', 'danger')
        #     return redirect(url_for('admin.admin', tab='campus'))

        if isinstance(image, FileStorage) and image.filename != '':
            # campusinfoname = campusname.lower()
            # campusinfoname = campusinfoname.replace(' ', '-')
            path = os.path.join(imagepath, secure_filename(str(campusid) + '.jpg'))
            image.save(path)

        for subject in request.form.getlist('subjects'):
            if subject.isdigit() and subject:
                campussubject = CampusSubject(campusinfo_id=int(campusid), subject_id=int(subject))
                print(campussubject)
                db.session.add(campussubject)
                db.session.commit()

        campus = CampusInfo.query.filter_by(id=campusid).first()
        campus.name = campusname
        db.session.commit()
    return redirect(url_for('admin.admin', tab='campus'))


UPLOAD_FOLDER = 'static/images/pictographs'
ALLOWED_EXTENSIONS = {'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_blueprint.route('/subjects', methods=['POST'])
@login_required
def subjects():
    if request.method == "POST":
        subjectname = request.form.get('add_subjectname')
        color = request.form.get('add_subjectcolor').replace('#', '')
        pictograph = request.files['add_subjectpictograph']

        subject = Subject(name=subjectname, color=color)
        subjectinfoname = subjectname.lower()

        if pictograph:
            print('-----this is never accessed-----')
            filename = secure_filename(pictograph.filename)
            filename = subjectinfoname + '.' + filename.rsplit('.', 1)[1].lower()
            pictograph.save(os.path.join(UPLOAD_FOLDER, filename))
            subject.image = filename

        db.session.add(subject)
        db.session.commit()

    return redirect(url_for('admin.admin', tab='subjects'))

@admin_blueprint.route('/subjects/<method>/<subjectid>', methods=["POST"])
@login_required
def update_subject(method, subjectid):
    if method.lower() == "delete":
        subject = Subject.query.filter_by(id=subjectid).first()

        campus_subjects = CampusSubject.query.filter_by(subject_id=subjectid).all()
        for campus_subject in campus_subjects:
            campusid = campus_subject.campusinfo_id
            update_campussubjects('remove', campusid, subjectid)
        
        for campuslog in CampusLog.query.filter_by(subject_id=subjectid).all():
            db.session.delete(campuslog)
            db.session.commit()

        for campuslog in CampusLog.query.filter_by(subject_id=subjectid).all():
            db.session.delete(campuslog)
            db.session.commit()
            
        db.session.delete(subject)
        db.session.commit()

    elif method.lower() == "put":
        subjectname = request.form.get('subjectname')
        color = request.form.get('subjectcolor')
        pictograph = request.files['subjectpictograph']
        reset_image = request.form.get('reset_image') 


        subject = Subject.query.filter_by(id=subjectid).first()


        # if isinstance(pictograph, FileStorage) and pictograph.filename != '':
        #     subjectinfoname = subjectname.lower()
        #     subjectinfoname = subjectinfoname.replace(' ', '-')
        #     path = os.path.join(UPLOAD_FOLDER, secure_filename(subjectinfoname + '.png'))
        #     pictograph.save(path)
        #     subject.image = secure_filename(subjectinfoname + '.png')

        if reset_image == "true":
            if subject.image and subject.image != 'imagePlaceholder.png':
                old_image_path = os.path.join(UPLOAD_FOLDER, subject.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            subject.image = 'imagePlaceholder.png'  

        elif pictograph and pictograph.filename != '':
            subjectinfoname = subjectname.lower().replace(' ', '-')
            new_image_filename = secure_filename(subjectinfoname + '.png')
            new_image_path = os.path.join(UPLOAD_FOLDER, new_image_filename)

            if subject.image and subject.image != 'imagePlaceholder.png':
                old_image_path = os.path.join(UPLOAD_FOLDER, subject.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            pictograph.save(new_image_path)
            subject.image = new_image_filename


        subject.name = subjectname
        subject.color = color.replace('#', '')

        db.session.commit()
    return redirect(url_for('admin.admin', tab='subjects'))


@admin_blueprint.route('/campussubjects/<method>/<campusid>/<subjectid>', methods=['POST', 'GET'])
@login_required
def update_campussubjects(method, campusid, subjectid):
    if method.lower() == 'remove':
        campussubject = CampusSubject.query.filter_by(campusinfo_id=campusid, subject_id=subjectid).first()
        db.session.delete(campussubject)
        db.session.commit()
    elif method.lower() == 'add':
        campussubject = CampusSubject(campusinfo_id=campusid, subject_id=subjectid)
        db.session.add(campussubject)
        db.session.commit()
    return redirect(url_for('admin.admin', tab='campus'))