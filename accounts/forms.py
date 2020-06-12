from django import forms
from django.contrib.auth import get_user_model
from .models import *
import pyodbc

User = get_user_model()
conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=192.168.10.16;DATABASE=sugarcrm_configuration;UID=powerbi;PWD=poweruser@1234567')
cursor = conn.cursor()
print("Connected")
cursor.execute('SELECT name FROM sugarcrm_configuration.dbo.tbl_int_user where status = 1 order by name')


NAME_CHOICES = [tuple([x[0],x[0]]) for x in cursor]

class RegForm(forms.ModelForm):
	name = forms.CharField(widget=forms.Select(choices=NAME_CHOICES))
	class Meta:
		model = Employees
		fields = ('name',)


class LoginForm(forms.Form):
    admn_no = forms.CharField(max_length=8)
    password = forms.CharField(widget=forms.PasswordInput())