from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.contrib.auth.models import User
from .models import Lecture, Question
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


@login_required(login_url="application:signup")
def home(request):
    template = loader.get_template('application/home.html')
    context={
        'lectures' : Lecture.objects.all(),
        'questions' : Question.objects.all(),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:signup")
def mod_panel(request):
    return None


@login_required(login_url="application:signup")
def lecturer_panel(request):
    return None


@login_required(login_url="application:signup")
def user_panel(request):
    return None


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is None:
                return render(request, 'application/login.html', {'form': form, 'pass_incorrect': True})
            login(request, user)
            return HttpResponseRedirect(reverse('application:home'))
    else:
        form = LoginForm()
    return render(request, 'application/login.html', {'form': form, 'pass_incorrect': False})


def user_logout(request):
    return None


def user_signup(request):
    return None
