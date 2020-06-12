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
            total = 0
            directory = str(usr)
            parent = "Dataset/"
            path = os.path.join(parent, directory)
            try:
                os.mkdir(path)
                print("[INFO] Directory Created")
            except:
                messages.info(request, "Dataset of selected user already exsists")
                return redirect('/cds/')
            
            try:
                #cam = VideoStream(config.incamera).start()
                vs = cv2.VideoCapture(config.incamera)
                print("[INFO] starting video stream...")
            except:
                messages.info(request, "Camera not found")
                return redirect('/')
            faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            
            

            time.sleep(5.0)

            while True:
                ret, frame = vs.read()
                orig = frame.copy()
                frame = imutils.resize(frame, width=400)
                rects = detector.detectMultiScale(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
                    minNeighbors=5, minSize=(30, 30))
                cv2.imshow("Frame", frame)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in  faces:
                    key = cv2.waitKey(1) & 0xFF
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
