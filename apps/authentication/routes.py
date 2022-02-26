# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from turtle import circle
import pandas as pd
import numpy as np
import datetime
import urllib.request
import cv2
from flask import render_template, redirect, request, url_for, Response, session
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from models.detector import face_detector
from models.verifier.face_verifier import FaceVerifier
from apps import db, login_manager
from apps.authentication import blueprint
from flask import current_app
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users,Students,InfoClass
from apps.authentication.util import verify_pass
from run import app
import tensorflow as tf
from multiprocessing import Pool
import itertools

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.attendance'))

#-------------------------------------------------------------------------------------
global fd
fd = face_detector.FaceAlignmentDetector(
    lmd_weights_path="./models/detector/FAN/2DFAN-4_keras.h5"# 2DFAN-4_keras.h5, 2DFAN-1_keras.h5
)
global fv
fv = FaceVerifier(classes=512, extractor = "facenet")
fv.set_detector(fd)
global students
students=Students.query.all()
global img_crop
global graph
graph = tf.get_default_graph()


def resize_image(im, max_size=768):
    if np.max(im.shape) > max_size:
        ratio = max_size / np.max(im.shape)
        print(f"Resize image to ({str(int(im.shape[1]*ratio))}, {str(int(im.shape[0]*ratio))}).")
        return cv2.resize(im, (0,0), fx=ratio, fy=ratio)
    return im
def addInfo_In(msv):
    with app.app_context():
        if (db.session.query(InfoClass).filter(InfoClass.msv==msv).count()%2==0):
            x = datetime.datetime.now()
            id=db.session.query(InfoClass).count()
            student = InfoClass(id+1,msv,x,'In')
            db.session.add(student)
            db.session.commit()
def addInfo_Out(msv):
    with app.app_context():
        if (db.session.query(InfoClass).filter(InfoClass.msv==msv).count()%2==1):
            x = datetime.datetime.now()
            id=db.session.query(InfoClass).count()
            student = InfoClass(id+1,msv,x,'Out')
            db.session.add(student)
            db.session.commit()
def Verifiert(im1,im2):
    global fv  
    with graph.as_default():
        result, distance = fv.verify(im1, im2, threshold=0.5, with_detection=False, with_alignment=False, return_distance=True)
    return result,distance
def VerifierStudent(student): 
    global fv  
    # print('1')
    url=student.img
    response = urllib.request.urlopen(url)
    image = np.asarray(bytearray(response.read()), dtype="uint8")
    im_known = cv2.imdecode(image, cv2.IMREAD_COLOR)
    im_known = resize_image(im_known)
    kq=[]
    # result, distance=Verifiert(im_known,img_crop)
    # print('2')
    return kq

def gen_frames():
    global students
    global img_crop
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FPS, 5)
    num_people=1000

    stu_new=[]
    stu_old=[]
    while True:
        success,frame=camera.read()
        
        if not success:
            break
        else:
            imgS=cv2.resize(frame,(0,0),None,0.25,0.25)
            imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
            with graph.as_default():
                bboxes = fd.detect_face(imgS, with_landmarks=False)

            for i in bboxes:
            #     # Display detected face
                if (len(i)>0):
                    x0, y0, x1, y1,score = i
                    x0, y0, x1, y1=x0*4, y0*4, x1*4, y1*4
                    x0, y0, x1, y1 = map(int, [x0, y0, x1, y1])

                    width1,width2,height1,height2=x0-50,x1+10,y0-20,y1+20
                    if(width1<0):
                        width1=0
                    if(height1<0):
                        height1=0
                    if(width2>frame.shape[0]):
                        width2=frame.shape[0]
                    if(height2>frame.shape[1]):
                        height2=frame.shape[1]
                    img_crop = frame[width1:width2, height1:height2, :]
                    img_crop = resize_image(img_crop) 
                    img_crop=cv2.cvtColor(img_crop,cv2.COLOR_BGR2RGB)
                    distance_test=10000
                    name="Unknown"

                    # pool = Pool()
                    # result=pool.map(VerifierStudent, students)
                    
                    # pool.close()
                    # pool.join()

                    
                    for student in students:
                        
                        url=student.img
                        response = urllib.request.urlopen(url)
                        image = np.asarray(bytearray(response.read()), dtype="uint8")
                        im_known = cv2.imdecode(image, cv2.IMREAD_COLOR)
                        im_known = resize_image(im_known)
                        
                        # with graph.as_default():
                        #     result, distance = fv.verify(im_known, img_crop, threshold=0.5, with_detection=False, with_alignment=False, return_distance=True)
                        # print("aaaaaaaaaaaaaaaaaaa")
                        result, distance=Verifiert(im_known,img_crop)
                        
                        if distance<distance_test:
                            name=student.msv
                        distance_test=distance
                        
                    if(distance_test>1.0):
                        name="Unknown"
                    if name!="Unknown":    
                        addInfo_In(name)
                        stu_new.append(name)
                    
                    cv2.rectangle(frame, (y0, x0), (y1, x1), (200, 0, 200), 4)
                    cv2.rectangle(frame, (y0, x0 + 35), (y1, x0), (200, 0, 200), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name , (y0 + 6, x0 +25), font, 1.0, (255, 255, 255), 1)
                    cv2.putText(frame, str(round(distance_test,4)) , (y0 + 6, x0 -10), font, 1.0, (255, 0, 255), 1)
            
            for i in stu_old:
                if i not in stu_new:
                    addInfo_Out(i)
            stu_old=stu_new
            stu_new=[]
            
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@blueprint.route('/end')
def end():
    for student in students:
        addInfo_Out(student.msv)
    return redirect(url_for('authentication_blueprint.login'))
@blueprint.route('/attendance')
def attendance():
    return render_template('face_recognition/face.html')
@blueprint.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#-------------------------------------------------------------------------------------

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('home_blueprint.index'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register.html', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        photo = request.form['photo']
        
        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)

@blueprint.route('/profile')
def profile():
    return render_template('accounts/profile.html',user=current_user)
@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))




@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
