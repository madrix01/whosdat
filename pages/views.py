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

from .models import *
from .forms import *

from imutils.video import VideoStream, FPS
from imutils import paths


User = get_user_model()

def index(request):
    context = {}
    return render(request, 'pages/index.html', context)

@login_required
def create_dataset(request):
    if request.method == "POST":
        form = DataForm(request.POST)
        if form.is_valid():
            start_time = time.time()
            imageCtr = 0
            print("[INFO] Is valid")
            usr = form.cleaned_data['usr']
            dataset = "Dataset/{usr}"
            x = UserData(usr=usr, dataset=dataset)
            x.save()
            detector = cv2.CascadeClassifier("opencv_haarcascade_data/haarcascade_frontalface_default.xml")
            print("[INFO] starting video stream...")
            #vs = VideoStream("rtsp://admin:admin1234@192.168.:554/cam/realmonitor?channel=1&subtype=1").start()
            vs = VideoStream("rtsp://admin:Local@ssminfotech@192.168.16.69:554/cam/realmonitor?channel=1&subtype=1").start()
            time.sleep(5.0)
            total = 0
            directory = str(usr)
            parent = "Dataset/"
            path = os.path.join(parent, directory)
            try:
                os.mkdir(path)
                print("[INFO] Directory Created")
            except:
                pass

            while True:
                frame = vs.read()   
                orig = frame.copy()
                frame = imutils.resize(frame, width=400)
                rects = detector.detectMultiScale(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
                    minNeighbors=5, minSize=(30, 30))
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if time.time() - start_time >= 2:
                    p = parent + directory + "/" + str(imageCtr) + ".png" 
                    cv2.imwrite(p, orig)
                    imageCtr += 1
                    print("[INFO] ",p, "saved")
                    start_time = time.time()
                    if imageCtr == 31:
                        break
                if key == ord("q"):
                    break
            print("[INFO] {} face images stored".format(imageCtr))
            print("[INFO] cleaning up...")
            cv2.destroyAllWindows()
            vs.stop()
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
    return redirect("/")


def detect(request):
    print("[INFO] loading encodings + face detector...")
    data = pickle.loads(open("encodings.pickle", "rb").read())
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    print("[INFO] starting video stream...")
    vs = VideoStream("rtsp://admin:Local@ssminfotech@192.168.16.69:554/cam/realmonitor?channel=1&subtype=1").start()
    time.sleep(2.0)
    fps = FPS().start()
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=500, height=500)
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

        """for name in names:
                                    usr = User.objects.get(admn_no=name)
                                    x = Attendance(usr=usr)"""
        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        print(names)
        context = {
            'names' : str(names)
        }
        asyncio.sleep(1)
        if key == ord("q"):
            #x.save()
            break
        fps.update()
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    cv2.destroyAllWindows()
    vs.stop()
    return render(request, "pages/detect.html", context)
