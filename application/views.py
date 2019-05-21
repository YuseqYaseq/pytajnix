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
import csv


@login_required(login_url="application:user_login")
def home(request):
    redirection_path = get_redirection_for_user(request.user)
    return HttpResponseRedirect(reverse(redirection_path))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def mod_panel(request):
    template = loader.get_template('application/mod_panel.html')
    moderator = request.user.moderator
    context = {
        'moderator_name': request.user.username,
        'lectures': list(moderator.moderated_lectures.filter(closed=False)),
        'closed_lectures': list(moderator.moderated_lectures.filter(closed=True))
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def mod_panel_lecture(request, lecture_id):
    moderator = request.user.moderator
    if not moderator.moderated_lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    lecture = Lecture.objects.filter(hash=lecture_id).first()
    if lecture.closed is True:
        return HttpResponseRedirect(reverse('application:mod_panel'))
    template = loader.get_template('application/mod_panel_lecture.html')
    if lecture.moderated:
        questions = list(Question.objects.filter(event=lecture_id, approved=False))
    else:
        questions = []
    for question in questions:
        question.votes_value = question.count_votes()
    context = {
        'moderator_name': request.user.username,
        'questions': questions,
        'lecture_id': lecture_id
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def mod_export_lecture(request, lecture_id):
    moderator = request.user.moderator
    if not moderator.moderated_lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    lecture = Lecture.objects.filter(hash=lecture_id).first()
    if not lecture.closed:
        return HttpResponse('Unauthorized', status=401)

    return export_lecture(lecture, lecture_id)


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def question_approval(request, lecture_id, question_id):
    moderator = request.user.moderator
    if not moderator.moderated_lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    lecture = moderator.moderated_lectures.filter(hash=lecture_id).first()
    if Question.objects.filter(pk=question_id):
        question = Question.objects.filter(pk=question_id).first()
        if lecture.question_set.filter(pk=question_id):
            question.approved = True
            question.save()
    return HttpResponseRedirect(reverse('application:mod_panel_lecture', args=(lecture_id,)))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'moderator'))
def lecture_close(request, lecture_id):
    moderator = request.user.moderator
    if not moderator.moderated_lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    lecture = moderator.moderated_lectures.filter(hash=lecture_id).first()
    if lecture.closed is False:
        lecture.closed = True
        lecture.save()
    return HttpResponseRedirect(reverse('application:mod_panel'))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'lecturer'))
def lecturer_panel(request):
    template = loader.get_template('application/lecturer_panel.html')
    lecturer = request.user.lecturer
    context = {
        'lecturer_name': '{} {}'.format(lecturer.name, lecturer.surname),
        'lecturer_title': lecturer.title,
        'lectures': list(lecturer.lectures.filter(closed=False)),
        'closed_lectures': list(lecturer.lectures.filter(closed=True))
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'lecturer'))
def lecturer_panel_lecture(request, lecture_id):
    lecturer = request.user.lecturer
    if not lecturer.lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    lecture = Lecture.objects.filter(hash=lecture_id)
    if not lecture or lecture.first().closed is True:
        return HttpResponseRedirect(reverse('application:mod_panel'))
    template = loader.get_template('application/lecturer_panel_lecture.html')
    if lecture.first().moderated:
        questions = list(Question.objects.filter(event=lecture_id, approved=True))
    else:
        questions = []
    for question in questions:
        question.votes_value = question.count_votes()
    context = {
        'direct_messages': list(DirectMessage.objects.filter(receiver=lecturer.id, event_id=lecture_id)),
        'questions': questions,
        'lecture_id': lecture_id,
        'allow_direct_questions': lecture.first().direct_questions_allowed,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'lecturer'))
def lecturer_export_lecture(request, lecture_id):
    lecturer = request.user.lecturer
    if not lecturer.lectures.filter(hash=lecture_id):
        return HttpResponse('Unauthorized', status=401)
    lecture = Lecture.objects.filter(hash=lecture_id).first()
    if not lecture.closed:
        return HttpResponse('Unauthorized', status=401)

    return export_lecture(lecture, lecture_id)


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
    context = {'user_name': participant_name, 'form': form, 'id_incorrect': id_incorrect}
    return render(request, 'application/user_panel.html', context)


@login_required(login_url="application:user_login")
@user_passes_test(lambda user: hasattr(user, 'participant'))
def user_panel_lecture(request, lecture_id):
    if not Lecture.objects.filter(hash=lecture_id) or Lecture.objects.filter(hash=lecture_id).first().closed is True:
        return HttpResponseRedirect(reverse('application:user_panel'))
    lecture = Lecture.objects.filter(hash=lecture_id).first()
    participant = request.user.participant
    template = loader.get_template('application/user_panel_lecture.html')
    questions = list(Question.objects.filter(event=lecture_id))
    for question in questions:
        question.votes_value = question.count_votes()
        question.user_can_vote = question.can_vote(request.user)
    context = {
        'user_nick': participant.public_nickname,
        'user_name': request.user.username,
        'direct_messages': DirectMessage.objects.filter(creator=request.user.id, event__hash=lecture_id),
        'questions': questions,
        'lecture_id': lecture_id,
        'allow_direct_questions': lecture.direct_questions_allowed,
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


def export_lecture(lecture, lecture_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + lecture.title + '.csv"'

    writer = csv.writer(response)
    writer.writerow([lecture.title, lecture.hash])
    writer.writerow(['Text', 'Tags', 'Votes', 'Approved'])
    for question in list(Question.objects.filter(event=lecture_id)):
        writer.writerow([question.text, question.tags, question.votes_value, question.approved])

    return response
