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
            admn_no = form.cleaned_data['admn_no']
            email = form.cleaned_data['email']
            q_mail = User.objects.filter(Q(email__iexact=email))
            q_admn = User.objects.filter(Q(admn_no__contains=admn_no))
            if q_admn.exists():
                raise forms.ValidationError('Admn_no already exsists')
            if q_mail.exists():
                raise forms.ValidationError('Email already exsists')
            else:
                password = form.cleaned_data['password']
                x = User(admn_no=admn_no, email=email)
                x.set_password(password)
                x.save()
                return redirect(reverse('accounts:login'))
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
