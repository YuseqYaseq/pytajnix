from django.db import transaction
from django.test import TestCase
from django.utils import timezone

# Create your tests here.
from application.models import Participant, Location, Lecture, Question, QuestionVote


class ModelTests(TestCase):

    def setUp(self):
        with transaction.atomic():
            location = Location(name='Centrum Informatyki', street='Kawiory', local_number='5', city='Krakow')
            location.save()
            lecture = Lecture(hash='3j7t950',
                              title='How to IT', start_time=timezone.now(),
                              end_time=timezone.now() + timezone.timedelta(hours=2),
                              location=location)
            lecture.save()

    def test_participant_save(self):
        participant = Participant(username='jkow', public_nickname='jkow')
        participant.save()
        self.assertTrue(Participant.objects.all().count() is 1)

    def test_lecture_create(self):
        saved = Lecture.objects.filter(title='How to IT').first()
        self.assertEquals('Centrum Informatyki', saved.location.name)

    def test_votes_count(self):
        with transaction.atomic():
            lecture = Lecture.objects.filter(hash='3j7t950').first()
            participant = Participant(username='jj', public_nickname='jj')
            participant.save()
            lecture.participants.add(participant)
            question = Question(text='How are you?', tags='hello', creator=participant, event=lecture)
            question.save()
            vote = QuestionVote(value=1, voter=participant, question=question)
            vote.save()
        question = Question.objects.all().first()
        self.assertEquals(question.count_votes(), 1)
