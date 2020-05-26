from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegForm(forms.ModelForm):
    admn_no = forms.CharField(max_length=8)
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('email', 'admn_no')


class LoginForm(forms.Form):
    admn_no = forms.CharField(max_length=8)
    password = forms.CharField(widget=forms.PasswordInput())