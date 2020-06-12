from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import pyodbc

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=192.168.10.16;DATABASE=sugarcrm_configuration;UID=powerbi;PWD=poweruser@1234567')
            curs = conn.cursor()
            sql_command = "SELECT ID FROM sugarcrm_configuration.dbo.tbl_int_user where name=" + "'" + str(name) +"'" 
            curs.execute(sql_command)
            for x in curs:
                employe_id = str(x[0])
            q_name = Employees.objects.filter(Q(name__contains=name))
            if q_name.exists():
                messages.info(request, "User already exsists")
                return redirect('/accounts/register/')
            x = Employees(name=name, employe_id=employe_id)
            x.save()
            return redirect(reverse('pages:cd'))
    else:
        form = RegForm()

    return render(request, 'accounts/register.html', {
        'form' : form
    })

@csrf_exempt
def loginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            admn_no = form.cleaned_data['admn_no']
            password = form.cleaned_data['password']
            qs = User.objects.filter(Q(admn_no__iexact=admn_no))
            if not qs.exists():
                raise forms.ValidationError("Invalid admn_no")
            user_obj = qs.first()
            if not user_obj.check_password(password):
                raise forms.ValidationError("Incorrect password")
            else:
                form.cleaned_data['user_obj'] = user_obj
                user = form.cleaned_data['user_obj']
                login(request, user)
                print('[LOGGED IN]')
                return redirect(reverse('pages:home'))
    else:
        form = LoginForm()
    return render(request, 'accounts/Login.html', {
        'form' : form,
    })

@csrf_exempt
def logoutView(request):
    logout(request)
    return redirect(reverse('accounts:login'))
