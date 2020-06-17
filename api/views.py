from django.shortcuts import render
from pages.models import *
from django.http import JsonResponse
from itertools import islice

def LastTenIn(request):
	last_ten = Attendance.objects.values('name', 'time').order_by('-id')[:10][::-1]
	return JsonResponse(last_ten, safe=False)

def LastTenOut(request):
	last_ten = AttendanceOut.objects.values('name', 'time').order_by('-id')[:10][::-1]
	return JsonResponse(last_ten, safe=False)
