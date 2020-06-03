from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import *

User = get_user_model()

class UserData(models.Model):
    usr = models.ForeignKey(Employees, on_delete=models.CASCADE)
    dataset = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    isVerified = models.BooleanField(default=False)

    def __str__(self):
        return self.usr.name
    

class Attendance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now=True)

    def __str__(self):
        return self.employee.name