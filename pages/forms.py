from django import forms
from .models import *
from accounts.models import *

class DataForm(forms.ModelForm):
    class Meta:
        model = UserData
        fields = ('usr',)