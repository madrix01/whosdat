from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            employe_id = form.cleaned_data['employe_id']
            q_id = Employees.objects.filter(Q(employe_id__contains=employe_id))
            if q_id.exists():
                raise forms.ValidationError('ID already exsists')
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
