from django.db import models
from django.contrib.auth.models import User

class Lecture(models.Model):
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(User, related_name='%(class)s_participants')
    location = models.CharField(max_length=100)
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_lecturer')

    def __str__(self):
        return self.title

class Question(models.Model):
    text = models.CharField(max_length=300)
    tags = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creator')
    voters = models.ManyToManyField(User, related_name='%(class)s_voters')
    event = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    def __str__(self):
        return self.text