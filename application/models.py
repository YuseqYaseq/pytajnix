import random

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

    RANDOM_HASH_LETTERS = 'abcdefghijklmnopqrstuwyz1234567890!@#$%^&*()-_=+'
    RANDOM_HASH_LEN = 10

    hash = models.CharField(max_length=16, primary_key=True)
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Participant, related_name='%(class)s_participants')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='%(class)s_location')

    def set_random_hash(self):
        hash_set = False
        while not hash_set:
            hash_proposal = self.__generate_random_hash(self.RANDOM_HASH_LEN)
            if not self.__hash_exists_in_db(hash_proposal):
                self.hash = hash_proposal
                hash_set = True

    def __generate_random_hash(self, length=8):
        result = []
        for i in range(0, length):
            result.append(random.choice(self.RANDOM_HASH_LETTERS))
        return ''.join(result)

    def __hash_exists_in_db(self, hash_value):
        return len(Lecture.objects.filter(pk=hash_value)) > 0

    def __str__(self):
        return self.title


class Lecturer(User):
    title = models.CharField(max_length=50, null=True)
    lectures = models.ManyToManyField(Lecture, related_name='%(class)s_lectures')

    def add_lecture(self, lecture, save=True):
        self.lectures.add(lecture)
        if save:
            self.save()

    def add_lectures(self, lectures):
        for lecture in lectures:
            self.add_lecture(lecture, save=False)
        self.save()

    def __str__(self):
        title = self.title if self.title is not None else ''
        return '{} {} {}'.format(title, self.first_name, self.last_name)


class Moderator(User):
    moderated_lectures = models.ManyToManyField(Lecture, related_name='%(class)s_moderated_lectures')

    def add_lecture(self, lecture, save=True):
        self.moderated_lectures.add(lecture)
        if save:
            self.save()

    def add_lectures(self, lectures):
        for lecture in lectures:
            self.add_lecture(lecture, save=False)
        self.save()


class Administrator(User):
    # to be used in the future
    pass


class Question(models.Model):
    text = models.CharField(max_length=300)
    tags = models.CharField(max_length=200)
    creator = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creator')
    voters = models.ManyToManyField(Participant, related_name='%(class)s_voters', through='QuestionVote')
    event = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True)

    class CannotAddVote(Exception):
        pass

    def count_votes(self):
        result = 0
        for voter in self.voters.all():
            vote = QuestionVote.objects.get(question=self, voter=voter)
            result += vote.value
        return result

    def add_vote(self, voter, vote_value):
        if not self.can_vote(voter):
            raise Question.CannotAddVote('Vote already added by the voter')
        QuestionVote.objects.create(voter=voter,
                                    question=self,
                                    value=vote_value)

    def remove_vote(self, voter):
        vote = QuestionVote.objects.get(question=self, voter=voter)
        vote.delete()

    def can_vote(self, voter):
        return self.voters.filter(pk=voter.id).count() is 0

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
