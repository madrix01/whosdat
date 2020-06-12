from datetime import datetime
import time
import cv2
import imutils
import os
import pickle
import asyncio
import numpy as np
import face_recognition

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http.response import StreamingHttpResponse
from django.contrib import messages

from accounts.models import *
from .models import *
from .forms import *
import config

from imutils.video import VideoStream, FPS
from imutils import paths
import pyodbc

def get_sec(time_str):
    time_str = str(time_str)
    h, m, s = time_str.split(':')
    return float(h)*3600 + float(m)*60 + float(s)

User = get_user_model()

def noCamera(request):
    return render(request, '')

def index(request):
    context = {}
    return render(request, 'pages/index.html', context)


def cds(request):
    if request.method == "POST":
        form = DataForm(request.POST)
        if form.is_valid():
            start_time = time.time()
            sampleNum = 0
            
            usr = form.cleaned_data['usr']
            dataset = "Dataset/{usr}"
            x = UserData(usr=usr, dataset=dataset)
            x.save()
            
            directory = str(usr)
            parent = "Dataset/"
            path = os.path.join(parent, directory)
            try:
                os.mkdir(path)
                print("[INFO] Directory Created")
            except:
                messages.info(request, "Dataset of selected user already exsists")
                return redirect('/create_dataset/')
            time.sleep(2.0)
            try:
                cam = cv2.VideoCapture(config.incamera)
                print("[INFO] starting video stream...")
            except:
                messages.info(request, "Camera not found")
                return redirect('/')
            faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            time.sleep(2.0)
            while(True):
                ret, img = cam.read()
                img = img[0:400 , 185:420]
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceDetect.detectMultiScale(gray, 1.3, 5)
                for(x,y,w,h) in faces:
                    p = parent + directory + "/" + str(sampleNum) + ".png"
                    print(p)
                    cv2.imwrite(p, img)
                    cv2.rectangle(img,(x,y),(x+w,y+h), (0,255,0), 2)
                    cv2.waitKey(250)
                    start_time = time.time()
                    sampleNum = sampleNum+1
                cv2.imshow("Face",img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or sampleNum == 30:
                    break
            cam.release()
            cv2.destroyAllWindows()
    else:
        form = DataForm()
    context = {'form': form}
    return render(request, "pages/create_dataset.html", context)



def train(request):
    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images("Dataset"))
    knownEncodings = []
    knownNames = []
    for (i, imagePath) in enumerate(imagePaths):
        print("[INFO] processing image {}/{}".format(i + 1,
            len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb,
            model="hog") 
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:

            knownEncodings.append(encoding)
            knownNames.append(name)
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()
    messages.info(request, "Dataset Trained")
    return redirect('/')

def detect(request):
    redirect('/')
    print("[INFO] loading encodings + face detector...")
    data = pickle.loads(open("encodings.pickle", "rb").read())
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    print("[INFO] starting video stream...")
    try:
        vs = VideoStream(config.incamera).start()
        print("[INFO] Opened")
        redirect('/')
    
    except:
        print("[INFO] No Camera online")

        redirect('/')
    

    time.sleep(2.0)
    fps = FPS().start()
    st_time = time.time()
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        frame = frame[0:300 , 190:400]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"],
                encoding)
            name = "Unknown"
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
            names.append(name)

        for name in names:
            if name != 'Unknown':
                print(name)
                usr = Employees.objects.get(name=name)
                try:
                    at = Attendance.objects.filter(name=name).order_by('-id')[:1][::-1][0]
                except:
                    pass
                #l_time = time.strptime(at.time, '%H:%M:%S')
                #print(type(l_time), l_time)
                t = Attendance(employee=usr, name=usr.name)
                if time.time() - st_time >= 5 :
                    now = datetime.now()
                    now = now.strftime("%H:%M:%S")
                    t.save()
                    st_time = time.time()

        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        
        context = {
            'names' : str(names)
        }
        if key == ord("q"):
            break
        fps.update()
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    cv2.destroyAllWindows()
    vs.stop()
    return render(request, "pages/checkview.html", context)


def Attend(request):
    return render(request, 'pages/checkview.html', {})