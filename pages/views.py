from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import *
from .forms import *
import time
import cv2
from imutils.video import VideoStream, FPS
import imutils
from django.http.response import StreamingHttpResponse
import os
from recog.settings import BASE_DIR
import numpy as np
from imutils import paths
import face_recognition
import pickle
import asyncio

User = get_user_model()

def index(request):
    context = {}
    return render(request, 'pages/index.html', context)

@login_required
def create_dataset(request):
    if request.method == "POST":
        form = DataForm(request.POST)
        if form.is_valid():
            usr = form.cleaned_data['usr']
            dataset = "Dataset/{usr}"
            x = UserData(usr=usr, dataset=dataset)
            x.save()
            detector = cv2.CascadeClassifier("opencv_haarcascade_data/haarcascade_frontalface_default.xml")
            print("[INFO] starting video stream...")
            vs = VideoStream("rtsp://admin:admin1234@192.168.2.108:554/cam/realmonitor?channel=1&subtype=1").start()
            time.sleep(2.0)
            total = 0
            directory = str(usr)
            parent = "Dataset/"
            path = os.path.join(parent, directory)
            try:
                os.mkdir(path)    
            except:
                pass
            while True:
                frame = vs.read()
                orig = frame.copy()
                frame = imutils.resize(frame, width=400)
                rects = detector.detectMultiScale(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
                    minNeighbors=5, minSize=(30, 30))
                for (x, y, w, h) in rects:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("k"):
                    p = parent + directory + "/" + str(total) + ".png" 
                    cv2.imwrite(p, orig)
                    total += 1
                    print(p)
                elif key == ord("q"):
                    break
            print("[INFO] {} face images stored".format(total))
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
	# extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1,
            len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        # load the input image and convert it from RGB (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb,
            model="hog") 

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and
            # encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

# dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()
    return redirect("/")

def frame_detect(frame, detector, data):
    frame = imutils.resize(frame, width=500)
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
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
        # if key == ord("q"):
        #     break
    return 0

def detect(request):
    print("[INFO] loading encodings + face detector...")
    data = pickle.loads(open("encodings.pickle", "rb").read())
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    print("[INFO] starting video stream...")
    vs = VideoStream("rtsp://admin:admin1234@192.168.2.108:554/cam/realmonitor?channel=1&subtype=1").start()
    time.sleep(2.0)
    fps = FPS().start()
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
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
            break
        fps.update()
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    cv2.destroyAllWindows()
    vs.stop()
    return render(request, "pages/detect.html", context)
