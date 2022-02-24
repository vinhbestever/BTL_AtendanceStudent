# -*- coding: utf-8 -*-

import numpy as np
import urllib.request
import cv2
from models.detector import face_detector
from models.verifier.face_verifier import FaceVerifier

def resize_image(im, max_size=768):
    if np.max(im.shape) > max_size:
        ratio = max_size / np.max(im.shape)
        print(f"Resize image to ({str(int(im.shape[1]*ratio))}, {str(int(im.shape[0]*ratio))}).")
        return cv2.resize(im, (0,0), fx=ratio, fy=ratio)
    else:
        return im
# url="https://scontent.fhan5-9.fna.fbcdn.net/v/t39.30808-1/c0.0.160.160a/p160x160/271153042_1012777712609393_6682807788287512087_n.jpg?_nc_cat=109&ccb=1-5&_nc_sid=7206a8&_nc_ohc=7RG4W2gWhqMAX_vdsgy&_nc_ht=scontent.fhan5-9.fna&oh=00_AT8CwyZohemL_cuoEGi1qhzgstBSUi0smsgFGDfgZiKGeQ&oe=61F69C91"
# response = urllib.request.urlopen(url)
# image = np.asarray(bytearray(response.read()), dtype="uint8")
# im1 = cv2.imdecode(image, cv2.IMREAD_COLOR)
# im1 = resize_image(im1)
im1 = cv2.imread("image_train/vinh2.jpg")[..., ::-1]
im1 = resize_image(im1) 
url2="https://img.nhandan.com.vn/Files/Images/2021/09/12/CR-1631402073570.jpg"
response2 = urllib.request.urlopen(url2)
image2 = np.asarray(bytearray(response2.read()), dtype="uint8")
im2 = cv2.imdecode(image2, cv2.IMREAD_COLOR)
cv2.imshow('Webcam',im2)
im2 = resize_image(im2)
students_table=[
    im1,
    im2,
    
]
students_name=[
    'Ronaldo',
    'Vinh',
    
]
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FPS, 5)
fd = face_detector.FaceAlignmentDetector(
    lmd_weights_path="./models/detector/FAN/2DFAN-4_keras.h5"# 2DFAN-4_keras.h5, 2DFAN-1_keras.h5
)
fv = FaceVerifier(extractor="facenet")
fv.set_detector(fd)
# while True:
#     success,frame=camera.read()
    
#     imgS=cv2.resize(frame,(0,0),None,0.25,0.25)
#     imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
#     bboxes = fd.detect_face(imgS, with_landmarks=False)
    

#     for i in bboxes:
#         # Display detected face
#         if (len(i)>0):
#             # print(i)
            
#             x0, y0, x1, y1,score = i
#             x0, y0, x1, y1=x0*4, y0*4, x1*4, y1*4
#             x0, y0, x1, y1 = map(int, [x0, y0, x1, y1])
            
#             width1,width2,height1,height2=x0-50,x1+10,y0-20,y1+20
#             if(width1<0):
#                 width1=0
#             if(height1<0):
#                 height1=0
#             if(width2>frame.shape[0]):
#                 width2=frame.shape[0]
#             if(height2>frame.shape[1]):
#                 height2=frame.shape[1]
#             # print(width1,width2,height1,height2)
#             # print(frame.shape)
#             img_crop = frame[width1:width2, height1:height2, :]
#             img_crop = resize_image(img_crop) 
#             count=0
#             distance_test=10000
#             name="Unknown"
#             for img in students_table:
#                 result, distance = fv.verify(img, img_crop, threshold=0.5, with_detection=False, with_alignment=False, return_distance=True)

#                 if result:
#                     if distance<distance_test:
#                         name=students_name[count]
#                     distance_test=distance
#                 count+=1
#             # print(frame.shape)
#             cv2.rectangle(frame, (y0, x0), (y1, x1), (200, 0, 200), 4)
#             cv2.rectangle(frame, (y0, x0 + 35), (y1, x0), (200, 0, 200), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (y0 + 6, x0 +25), font, 1.0, (255, 255, 255), 1)

#     cv2.imshow('Webcam',frame)
#     cv2.waitKey(1)