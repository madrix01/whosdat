from django.shortcuts import render
from .camera import VideoCamera, IPWebCam
from django.http.response import StreamingHttpResponse

def index(request):
    context = {}
    return render(request, "main/home.html", context)

