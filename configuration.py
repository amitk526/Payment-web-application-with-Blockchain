from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True} 
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True, index=True)
    password = db.Column(db.String(50))
    dateofreg = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, email, password):
        self.email = email
        self.password = password
       
class Profile(db.Model):
    __tablename__ = "profile"
    __table_args__ = {'extend_existing': True} 
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    puid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    aadhar_no = db.Column(db.String(13))
    phone_no = db.Column(db.String(10))
    acc_no = db.Column(db.String(13))
    balance = db.Column(db.String())

    def __init__(self, puid, firstname, lastname, aadhar_no, phone_no, acc_no, balance):
        self.puid = puid
        self.firstname = firstname
        self.lastname = lastname
        self.aadhar_no = aadhar_no
        self.phone_no = phone_no
        self.acc_no = acc_no
        self.balance = balance
        
class Transactions(db.Model):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True} 
    tid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tuid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    debit = db.Column(db.String())
    credit = db.Column(db.String())
    balance = db.Column(db.String())
    dateoftrans = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, tuid, debit, credit, balance):
        self.tuid = tuid
        self.debit = debit
        self.credit = credit
        self.balance = balance
