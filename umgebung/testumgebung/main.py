from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from passlib.hash import sha256_crypt
import os
from dotenv import load_dotenv
from models import db
from models import CampusInfo, Subject, CampusSubject, Account
from datetime import timedelta
from admin import admin_blueprint, data_blueprint


load_dotenv()

app = Flask(__name__)
login_manager = LoginManager()

db_username = os.environ.get('DATABASE_USERNAME')
db_password = os.environ.get('DATABASE_PASSWORD')
db_host = os.environ.get('DATABASE_HOST', "localhost")
db_name = os.environ.get('DATABASE_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=90)
app.config['UPLOAD_FOLDER'] = "static/uploads/"

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")   
login_manager.login_view = "data.login"

db.init_app(app=app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()
    # Check if admin account exists
    if Account.query.filter_by(username="admin").first() is None:
        admin = Account(firstname="Admin", surname="Account", username="admin", password=sha256_crypt.hash("admin"))
        db.session.add(admin)
        db.session.commit()

app.register_blueprint(admin_blueprint)
app.register_blueprint(data_blueprint)


@login_manager.user_loader
def load_user(user_id):
    return Account.query.filter_by(id = user_id).first()


@app.route('/')
@login_required
def index():
    campuses = CampusInfo.query.all()
    return render_template('index.html', campuses=campuses)


@app.route('/campuses/<name>')
@login_required
def campuses(name):
    # Convert the URL-friendly name into the proper format for lookup
    campusinfoname = name.replace('-', ' ').title()

    # Retrieve the campus based on its name (case insensitive)
    campus = CampusInfo.query.filter(CampusInfo.name.ilike(campusinfoname)).first()

    # If no campus is found, return a 404 page
    if campus is None:
        return render_template('404.html')

    # Debugging: Print the campus ID to ensure correct campus is being queried
    print(f"Campus ID: {campus.id}, Campus Name: {campus.name}")

    # Now retrieve the campus subjects by campus ID
    campussubjects = CampusSubject.query.filter_by(campusinfo_id=campus.id).all()

    # Retrieve the subjects linked to this campus based on subject ID
    subjects = []
    for campussubject in campussubjects:
        subject = Subject.query.filter_by(id=campussubject.subject_id).first()
        if subject:
            subjects.append(subject)

    # Render the campus page with the correct subjects
    return render_template('campus.html', subjects=subjects, campus=campus)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def is_light_color(hex_color):
    hex_color = hex_color.lstrip('#')
    
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    
    def apply_gamma(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r = apply_gamma(r)
    g = apply_gamma(g)
    b = apply_gamma(b)
    
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    return luminance > 0.5

app.jinja_env.filters['is_light_color'] = is_light_color

# Change back when deploying/developing
# if __name__ == "__main__":
#     app.run(debug=True, host="127.0.0.1", port=3306)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="129.132.175.25", port=8080) 
