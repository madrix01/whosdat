from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserData(models.Model):
    usr = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    isVerified = models.BooleanField(default=False)

    def __str__(self):
        return self.usr.admn_no
    

class Attendance(models.Model):
    usr = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now=True)

    def __str__(self):
        return self.usr.admn_no