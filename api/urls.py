from django.urls import path
from . import views

urlpatterns = [
	path('api/in/', views.LastTenIn),
	path('api/out/', views.LastTenOut),
]