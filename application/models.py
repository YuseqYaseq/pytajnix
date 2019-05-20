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


class Participant(models.Model):
    public_nickname = models.CharField(max_length=200, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participant')


class Lecture(models.Model):

    RANDOM_HASH_LETTERS = 'abcdefghijklmnopqrstuwyz1234567890'
    RANDOM_HASH_LEN = 10

    hash = models.CharField(max_length=16, primary_key=True)
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    moderated = models.BooleanField(default=False)
    direct_questions_allowed = models.BooleanField(default=True)
    closed = models.BooleanField(default=False)
    participants = models.ManyToManyField(Participant, related_name='%(class)s_participants', blank=True)
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


class Lecturer(models.Model):
    title = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=120, null=True)
    surname = models.CharField(max_length=120, null=True)
    lectures = models.ManyToManyField(Lecture, related_name='%(class)s_lecturers', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer')

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
        return '{} {} {}'.format(title, self.user.first_name, self.user.last_name)


class Moderator(models.Model):
    moderated_lectures = models.ManyToManyField(Lecture, related_name='%(class)s_moderated_lectures', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='moderator')

    def add_lecture(self, lecture, save=True):
        self.moderated_lectures.add(lecture)
        if save:
            self.save()

    def add_lectures(self, lectures):
        for lecture in lectures:
            self.add_lecture(lecture, save=False)
        self.save()


class Question(models.Model):
    text = models.CharField(max_length=300)
    tags = models.CharField(max_length=200)
    approved = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creator')
    voters = models.ManyToManyField(User, related_name='%(class)s_voters', through='QuestionVote', blank=True)
    event = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True)
    votes_value = 0
    user_can_vote = True

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
    voter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_voter')


class DirectMessage(models.Model):
    title = models.CharField(max_length=150)
    text = models.TextField(max_length=1500)
    date_time = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creator')
    event = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True, related_name='%(class)s_event')
    receiver = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, related_name='%(class)s_receiver')
