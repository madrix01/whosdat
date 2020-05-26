from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserData(models.Model):
    usr = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.CharField(max_length=100)

    def __str__(self):
        return self.usr
    