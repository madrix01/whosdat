from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import *
from .forms import *
import time
import cv2
from imutils.video import VideoStream
import imutils
from django.http.response import StreamingHttpResponse
import os
from recog.settings import BASE_DIR
import numpy as np


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
            vs = VideoStream(0).start()
            time.sleep(2.0)
            total = 0
            directory = str(usr)
            parent = "Dataset/"
            path = os.path.join(parent, directory)
            os.mkdir(path)
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