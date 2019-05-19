from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.contrib.auth.models import User

from application.utils.user_utils import get_redirection_for_user
from .models import Lecture, Question, DirectMessage, Participant
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth
from .forms import LoginForm, RegisterForm, LectureSelectionForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def mod_panel(request):
    template = loader.get_template('application/mod_panel.html')
    moderator = request.user.moderator
    context = {
        'moderator_name': request.user.username,
        'lectures': list(moderator.moderated_lectures.all())
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def mod_panel_lecture(request, lecture_id):
    moderator = request.user.moderator
    if not moderator.moderated_lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    template = loader.get_template('application/mod_panel_lecture.html')
    context = {
        'moderator_name': request.user.username,
        'questions': Question.objects.filter(event=lecture_id),
        'lecture_id': lecture_id
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'lecturer'))
def lecturer_panel(request):
    template = loader.get_template('application/lecturer_panel.html')
    lecturer = request.user.lecturer
    context = {
        'lecturer_name': '{} {}'.format(lecturer.name, lecturer.surname),
        'lecturer_title': lecturer.title,
        'lectures': list(lecturer.lectures.all())
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'lecturer'))
def lecturer_panel_lecture(request, lecture_id):
    lecturer = request.user.lecturer
    if not lecturer.lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    template = loader.get_template('application/lecturer_panel_lecture.html')
    context = {
        'direct_messages': DirectMessage.objects.filter(receiver=request.user.id),
        'questions': Question.objects.filter(event=lecture_id),
        'lecture_id': lecture_id,
        'allow_direct_questions': True,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'participant'))
def user_panel(request):
    id_incorrect = False
    participant_name = request.user.participant.public_nickname
    if request.method == 'POST':
        form = LectureSelectionForm(request.POST)
        if form.is_valid():
            lecture_id = form.cleaned_data['lecture_id']
            if not Lecture.objects.filter(hash=lecture_id):
                id_incorrect = True
            else:
                return HttpResponseRedirect(reverse('application:user_panel_lecture', args=(lecture_id, )))
    else:
        form = LectureSelectionForm()
    context = {'user_name': participant_name,'form': form, 'id_incorrect': id_incorrect}
    return render(request, 'application/user_panel.html', context)


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'participant'))
def user_panel_lecture(request, lecture_id):
    participant = request.user.participant
    template = loader.get_template('application/user_panel_lecture.html')
    context = {
        'user_nick': participant.public_nickname,
        'user_name': request.user.username,
        'direct_messages': DirectMessage.objects.filter(receiver=request.user.id),
        'questions': Question.objects.filter(event=lecture_id),
        'lecture_id': lecture_id,
        'allow_direct_questions': True,
    }
    return HttpResponse(template.render(context, request))


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is None:
                return render(request, 'application/login.html', {'form': form, 'pass_incorrect': True})
            login(request, user)
            redirection_path = get_redirection_for_user(user)
            return HttpResponseRedirect(reverse(redirection_path))
    else:
        form = LoginForm()
    return render(request, 'application/login.html', {'form': form, 'pass_incorrect': False})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('application:user_login'))


def user_signup(request):
    error = False
    err_message = ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            public_nickname = form.cleaned_data['public_nickname']
            try:
                user = User(username=username)
                user.set_password(password)
                user.save()
                participant = Participant(public_nickname=public_nickname, user=user)
                participant.save()
            except Exception as ex:
                return render(request, 'application/signup.html',
                              {'form': form, 'error': True, 'error_message': ex})

            return HttpResponseRedirect(reverse('application:user_login'))
        else:
            error = True
            err_message = 'Invalid form.'
    else:
        form = RegisterForm()
    return render(request, 'application/signup.html', {'form': form, 'error': error, 'error_message': err_message})
