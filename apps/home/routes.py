# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from unittest import result
from apps import db, login_manager
from apps.home import blueprint
from flask import render_template, redirect, request, url_for, Response
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home.forms import CreateStudent
from apps.authentication.models import InfoClass, Students,Users
import datetime
from sqlalchemy import cast, Date, extract
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
