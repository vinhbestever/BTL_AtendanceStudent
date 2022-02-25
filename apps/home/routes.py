# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from itertools import count
from unittest import result
from apps import db, login_manager
from apps.home import blueprint
from flask import render_template, redirect, request, url_for, Response
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home.forms import CreateStudent
from apps.authentication.models import InfoClass, Students,Users, Attendance,SummaryStudy
from apps.authentication.forms import EditAccountForm
import datetime
from sqlalchemy import cast, Date, extract
import hashlib
import binascii
import os

@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')
@blueprint.route('/add-student.html', methods=['GET', 'POST'])
@login_required
def add_student():
    create_student_form = CreateStudent(request.form)
    segment = get_segment(request)
    if 'add_student' in request.form:
        msv=request.form['msv']
        name=request.form['name']
        phone=request.form['phone']
        email=request.form['email']
        DOBs=request.form['DOBs']
        classes=request.form['classes']
        img=request.form['img']
        
        # check msv
        student = Students.query.filter_by(msv=msv).first()
        if student:
            return render_template('home/add-student.html',
                                   msg='Mã sinh viên đã tồn tại',
                                   success=False,
                                   form=create_student_form, segment=segment)
        # Check email exists
        student = Students.query.filter_by(email=email).first()
        if student:
            return render_template('home/add-student.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_student_form, segment=segment)

        student = Students(**request.form)
        db.session.add(student)
        db.session.commit()
        return render_template('home/add-student.html',
                               msg='Thêm sinh viên thành công',
                               success=True,
                               form=create_student_form, segment=segment)
    else:
        return render_template('home/add-student.html', form=create_student_form, segment=segment)
@blueprint.route('/edit_student/<string:msv>', methods=['GET', 'POST'])
@login_required
def edit_student(msv):
    create_student_form = CreateStudent(request.form)
    segment = get_segment(request)
    student = Students.query.filter_by(msv=msv).first()
    if 'edit_student' in request.form:
        msv=request.form['msv']
        name=request.form['name']
        phone=request.form['phone']
        email=request.form['email']
        DOBs=request.form['DOBs']
        classes=request.form['classes']
        img=request.form['img']
        
       

        x=db.session.query(Students).filter_by(msv=msv).first()
        x.msv=msv
        x.name=name
        x.phone=phone
        x.email=email
        x.DOBs=DOBs
        x.classes=classes
        x.img=img
        db.session.commit()
        return render_template('home/edit-student.html',
                               msg='Sửa thông tin sinh viên thành công',
                               success=True,
                               form=create_student_form, segment=segment,student=student)
    else:
        
        return render_template('home/edit-student.html', form=create_student_form, segment=segment,student=student)

@blueprint.route('/list-student.html', methods=['GET', 'POST'])
@login_required
def list_student():
    segment = get_segment(request)
    return render_template('home/list-student.html', rows=Students.query.all(), segment=segment)

def DeleteStudent(msv):
    sv=Students.query.filter_by(msv=msv).first()
    db.session.delete(sv)
    db.session.commit()
@blueprint.route('/delete_student/<string:msv>')
@login_required
def delete_student(msv):
    DeleteStudent(msv)
    return redirect(url_for('home_blueprint.list_student'))

@blueprint.route('/info_class', methods=['GET', 'POST'])
@login_required
def info_class():
    info=[]
    if 'search_time' in request.form:
        item=request.form
        timeinf= item["info-time"].split('-')
        
        info=db.session.query(InfoClass).filter(extract('year', InfoClass.time) == timeinf[2],extract('month', InfoClass.time) == timeinf[1],extract('day', InfoClass.time) == timeinf[0]).all()
        
    segment = get_segment(request)
    table = InfoClass.query.all()
    result=[]
    for time in table:
        a=time.time.date()
        result.append(a)
    result=list(set(result))

    return render_template('home/info-class.html', segment=segment, times=result, infos=info)

@blueprint.route('/attendance_check', methods=['GET', 'POST'])
@login_required
def attendance_check():
    info=[]
    if 'search_date' in request.form:
        item=request.form
        timeinf= item["info-time"].split('-')
        info=db.session.query(Attendance).filter(extract('year', Attendance.date) == timeinf[2],extract('month', Attendance.date) == timeinf[1],extract('day', Attendance.date) == timeinf[0]).all()
        
        if not info:
            stu=Students.query.all()
            for sv in stu:
                # print(sv.msv)
                temp=db.session.query(InfoClass).filter(extract('year', InfoClass.time) == timeinf[2]\
                    ,extract('month', InfoClass.time) == timeinf[1],extract('day', InfoClass.time)\
                    == timeinf[0],InfoClass.msv==sv.msv).all()
                if not temp:
                    status=False                   
                else:
                    sum=datetime.timedelta(minutes=0,seconds=0, microseconds=0)
                    for i in range(0,len(temp),2):
                        sum=sum+(temp[i+1].time-temp[i].time)
                    if sum.total_seconds() / 60 >=30:
                        status=True
                    else:
                        status=False
                id=db.session.query(Attendance).count()
                atten_time=datetime.datetime(int(timeinf[2]), int(timeinf[1]), int(timeinf[0]))
                student = Attendance(id+1,sv.msv,status,atten_time)
                db.session.add(student)
                db.session.commit()
            info=db.session.query(Attendance).filter(extract('year', Attendance.date) == timeinf[2],extract('month', Attendance.date) == timeinf[1],extract('day', Attendance.date) == timeinf[0]).all()
    segment = get_segment(request)
    table = InfoClass.query.all()
    result=[]
    for time in table:
        a=time.time.date()
        result.append(a)
    result=list(set(result))
    
    return render_template('home/list-attendance.html', segment=segment, times=result, infos=info)

@blueprint.route('/summany_study', methods=['GET', 'POST'])
@login_required
def summany_study():
    segment = get_segment(request)
    msg=False
    sum=[]
    if 'study_summany' in request.form:
        sum=SummaryStudy.query.all()
        if not sum:
            stu=Students.query.all()
            for sv in stu:
                temp=db.session.query(Attendance).filter(Attendance.msv==sv.msv).count()
                print(temp)
                if temp>=6:
                    status=True
                else:
                    status=False
                id=db.session.query(SummaryStudy).count()
                student = SummaryStudy(id+1,sv.msv,status)
                db.session.add(student)
                db.session.commit()
            sum=SummaryStudy.query.all()
        msg=True
    if 'delete_summany' in request.form:
        db.session.query(SummaryStudy).delete()
        db.session.commit()
        msg=False
    return render_template('home/summany.html', segment=segment, msg=msg, sum=sum)
@blueprint.route('/list-user', methods=['GET', 'POST'])
@login_required
def list_user():
    segment = get_segment(request)
    return render_template('home/list-account.html', rows=Users.query.all(), segment=segment)
def DeleteUser(id):
    sv=Users.query.filter_by(id=id).first()
    db.session.delete(sv)
    db.session.commit()
@blueprint.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    DeleteUser(id)
    return redirect(url_for('home_blueprint.list_user'))
@blueprint.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    create_student_form = EditAccountForm(request.form)
    segment = get_segment(request)
    user = Users.query.filter_by(id=id).first()
    if 'edit_user' in request.form:
        username=request.form['username']
        email=request.form['email']
        a=request.form['password']
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', a.encode('utf-8'),
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        password=(salt + pwdhash)
        role=request.form['role']

        x=db.session.query(Users).filter_by(id=id).first()
        x.username=username
        x.email=email
        x.password=password
        x.role=role
        db.session.commit()
        return render_template('home/edit-user.html',
                               msg='Sửa thông tin thành công',
                               success=True,
                               form=create_student_form, segment=segment,user=user)
    else:
        return render_template('home/edit-user.html', form=create_student_form, segment=segment,user=user)

@blueprint.route('/chart_analysis')
@login_required
def chart_analysis():
    segment = get_segment(request)
    info_table=InfoClass.query.all()
    labels1=['0','1','2','3','4','5','6','7','8','9']
    values1=[0,0,0,0,0,0,0,0,0,0]
    stu=Students.query.all()
    for sv in stu:
        temp=db.session.query(Attendance).filter(Attendance.msv==sv.msv,Attendance.attendance==1).count()
        values1[temp]+=1
    labels2=[]
    values2=[]
    for sv in stu:
        temp=db.session.query(InfoClass).filter(InfoClass.msv==sv.msv).all()
        sum=datetime.timedelta(minutes=0,seconds=0, microseconds=0)
        
        for i in range(0,len(temp),2):
            sum=sum+(temp[i+1].time-temp[i].time)
        hour=sum.total_seconds() / 360   
        labels2.append(sv.msv)  
        values2.append(hour) 
    labels3=[]
    values3=[]    
    for sv in stu:
        temp=db.session.query(Attendance).filter(Attendance.msv==sv.msv,Attendance.attendance==1).count()
        labels3.append(sv.msv)  
        values3.append(temp) 
    labels4=['Được thi','Cấm thi']
    values4=[]
    colors=["#46BFBD","#FF4500"]
    temp1=db.session.query(SummaryStudy).filter(SummaryStudy.status==1).count()
    temp2=db.session.query(SummaryStudy).filter(SummaryStudy.status==0).count()
    values4.append(temp1)
    values4.append(temp2)
    return render_template('home/chart-analysis.html', segment=segment, labels1=labels1, values1=values1,labels2=labels2, values2=values2,labels3=labels3, values3=values3,set=zip(values4, labels4, colors))
@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
