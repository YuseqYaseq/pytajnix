from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    name = models.CharField(max_length=200, null=True)
    street = models.CharField(max_length=80, null=True)
    local_number = models.CharField(max_length=40, null=True)
    city = models.CharField(max_length=80, null=True)
    room_number = models.CharField(max_length=40, null=True)

    def __str__(self):
        return self.name


class Participant(User):
    public_nickname = models.CharField(max_length=200, null=True)


class Lecture(models.Model):
    hash = models.CharField(max_length=16, primary_key=True)
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Participant, related_name='%(class)s_participants')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='%(class)s_location')

    def __str__(self):
        return self.title


class Lecturer(User):
    title = models.CharField(max_length=50, null=True)
    lectures = models.ManyToManyField(Lecture, related_name='%(class)s_lectures')

    def __str__(self):
        title = self.title if self.title is not None else ''
        return '{} {} {}'.format(title, self.first_name, self.last_name)


class Moderator(User):
    moderated_lectures = models.ManyToManyField(Lecture, related_name='%(class)s_moderated_lectures')


class Administrator(User):
    # to be used in the future
    pass


class Question(models.Model):
    text = models.CharField(max_length=300)
    tags = models.CharField(max_length=200)
    creator = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creator')
    voters = models.ManyToManyField(Participant, related_name='%(class)s_voters', through='QuestionVote')
    event = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True)

    def count_votes(self):
        result = 0
        for voter in self.voters.all():
            vote = QuestionVote.objects.get(question=self, voter=voter)
            result += vote.value
        return result

    def __str__(self):
        return self.text


class QuestionVote(models.Model):
    value = models.IntegerField(validators=[MaxValueValidator(1), MinValueValidator(-1)])
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, related_name='%(class)s_question')
    voter = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, related_name='%(class)s_voter')


class DirectMessage(models.Model):
    title = models.CharField(max_length=150)
    text = models.TextField(max_length=1500)
    date_time = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creator')
    event = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True, related_name='%(class)s_event')
    receiver = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, related_name='%(class)s_receiver')
