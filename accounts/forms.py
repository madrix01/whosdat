from django import forms
from django.contrib.auth import get_user_model
from .models import *
User = get_user_model()


class RegForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = "__all__"


class LoginForm(forms.Form):
    admn_no = forms.CharField(max_length=8)
    password = forms.CharField(widget=forms.PasswordInput())