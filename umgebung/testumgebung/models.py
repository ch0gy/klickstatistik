from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class CampusInfo(db.Model):
    __tablename__ = 'campusinfo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Campus: {%s' % self.id + ', ' + self.name + '}'

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    color = db.Column(db.String(6))
    image = db.Column(db.String(255))

    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return 'Subject: {%s' % self.id + ', ' + self.name + ', ' + self.color + '}'

class CampusSubject(db.Model):
    __tablename__ = 'campusinfo_subject'
    id = db.Column(db.Integer, primary_key=True)
    campusinfo_id = db.Column(db.Integer, db.ForeignKey('campusinfo.id'))
    campusinfo = db.relationship('CampusInfo', backref=db.backref('campusinfo_subject', lazy='dynamic'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject', backref=db.backref('subject_campus', lazy='dynamic'))

    def __init__(self, campusinfo_id, subject_id):
        self.campusinfo_id = campusinfo_id
        self.subject_id = subject_id

    def __repr__(self):
        return 'CampusSubject: {%s' % str(self.id) + ', ' + str(self.campusinfo) + ', ' + str(self.subject) + '}'

class CampusLog(db.Model):
    __tablename__ = 'campusinfo_log'
    id = db.Column(db.Integer, primary_key=True)
    campusinfo_id = db.Column(db.Integer, db.ForeignKey('campusinfo.id'))
    campusinfo = db.relationship('CampusInfo', backref=db.backref('campusinfo_log', lazy='dynamic'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject', backref=db.backref('subject_log', lazy='dynamic'))
    timestamp = db.Column(db.DateTime)

    def __init__(self, campusinfo_id, subject_id, timestamp):
        self.campusinfo_id = campusinfo_id
        self.subject_id = subject_id
        self.timestamp = timestamp

    def __repr__(self):
        return 'CampusLog: {%s' % str(self.id) + ', ' + str(self.campusinfo) + ', ' + str(self.subject) + ', ' + str(self.timestamp) + '}'

class Account(UserMixin, db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    firstname = db.Column(db.String(50))
    surname = db.Column(db.String(100))

    def __init__(self, username, password, firstname, surname):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.surname = surname

    def __repr__(self):
        return 'Account: {%s' % str(self.id) + ', ' + self.username + ', ' + self.password + ', ' + self.firstname + ', ' + self.surname + '}'