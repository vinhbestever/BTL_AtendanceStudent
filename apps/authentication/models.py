# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from importlib_metadata import email
from flask_login import UserMixin
from datetime import datetime
from apps import db, login_manager

from apps.authentication.util import hash_pass
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship
class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    photo = db.Column(db.String)
    role = db.Column(db.String(64), default='user') ## role {'user', 'docter', 'worker', 'teacher'}

    def __init__(self, **kwargs):
        
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)         

class Students(db.Model):
    __tablename__ = 'Students'

    msv=db.Column(db.String(64), primary_key=True)
    name=db.Column(db.String(64))  
    phone=db.Column(db.String(64))
    email= db.Column(db.String(64), unique=True)
    DOBs=db.Column(db.String(64))   
    classes=db.Column(db.String(64))
    img=db.Column(db.String(200))
    

    atten = relationship("Attendance", back_populates="relat_atten")
    in_out = relationship("InfoClass", back_populates="info")
    ban = relationship("SummaryStudy", back_populates="sum")

    def __init__(self,msv,name,phone,email,DOBs,classes,img, **kwargs):
        self.msv = msv
        self.name = name
        self.phone = phone
        self.email = email
        self.DOBs = DOBs
        self.classes = classes
        self.img = img
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.msv)         
    

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    msv=db.Column(db.String(64),ForeignKey('Students.msv')) 
    date=db.Column(db.DateTime())
    attendance=db.Column(db.Boolean()) 
    relat_atten = relationship("Students", back_populates="atten")

    def __init__(self,id,msv,attendance,date):
        self.id=id
        self.msv=msv
        self.attendance=attendance
        self.date=date

class InfoClass(db.Model):
    __tablename__ = 'InfoClass'
    id = db.Column(db.Integer, primary_key=True)
    msv=db.Column(db.String(64),ForeignKey('Students.msv'))
    time=db.Column(db.DateTime()) 
    status=db.Column(db.String(64)) 
    info = relationship("Students", back_populates="in_out")

    def __init__(self,id,msv,time,status):
        self.id=id
        self.msv=msv
        self.time=time
        self.status=status

class SummaryStudy(db.Model):
    __tablename__ = 'SummaryStudy'
    id = db.Column(db.Integer, primary_key=True)
    msv=db.Column(db.String(64),ForeignKey('Students.msv'))
    status=db.Column(db.Boolean()) 
    sum=relationship("Students", back_populates="ban")

    def __init__(self,id,msv,status):
        self.id=id
        self.msv=msv
        self.status=status


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
