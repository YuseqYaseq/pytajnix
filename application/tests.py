from django.db import transaction
from django.test import TestCase
from django.utils import timezone

# Create your tests here.
from application.models import Participant, Location, Lecture, Question, QuestionVote, Lecturer, Moderator


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
        _, _, question = self.__prepare_question_vote('jj')
        question = Question.objects.filter(pk=question.id).first()
        self.assertEquals(question.count_votes(), 1)

    def test_random_event_hash(self):
        location = Location.objects.filter(name='Centrum Informatyki').first()
        lecture = Lecture(title='Special', start_time=timezone.now(),
                          end_time=timezone.now() + timezone.timedelta(hours=2),
                          location=location)
        lecture.set_random_hash()
        lecture.save()
        created_lecture = Lecture.objects.filter(title='Special').count()
        self.assertEquals(created_lecture, 1)

    def test_lecturer_assign_lecture(self):
        lecturer = Lecturer.objects.create(title='PhD', first_name='Jan', last_name='Kowalski', username='phd_jkow')
        lecture = Lecture.objects.filter(pk='3j7t950').first()
        lecturer.add_lecture(lecture)
        lecturer = Lecturer.objects.filter(username='phd_jkow').first()
        self.assertEquals(lecturer.lectures.filter(pk='3j7t950').count(), 1)

    def test_lecturer_assign_moderator(self):
        moderator = Moderator.objects.create(first_name='Adam', last_name='Nowak', username='moderator')
        lecture = Lecture.objects.filter(pk='3j7t950').first()
        moderator.add_lecture(lecture)
        moderator = Moderator.objects.filter(username='moderator').first()
        self.assertEquals(moderator.moderated_lectures.filter(pk='3j7t950').count(), 1)

    def test_question_can_vote_1(self):
        participant, _, question = self.__prepare_question_vote('cj')
        participant = Participant.objects.filter(pk=participant.id).first()
        self.assertFalse(question.can_vote(participant))

    def test_question_can_vote_2(self):
        participant = Participant.objects.create(username='dd')
        lecture = Lecture.objects.get(hash='3j7t950')
        question = Question(text='How are you?', tags='hello', creator=participant, event=lecture)
        question.save()
        self.assertTrue(question.can_vote(participant))

    def test_add_vote_exception(self):
        with self.assertRaises(Question.CannotAddVote) as context:
            participant, lecture, question = self.__prepare_question_vote('md')
            question.add_vote(participant, 1)
            question.add_vote(participant, 1)

        self.assertTrue('Vote already added by the voter' in str(context.exception))

    def __prepare_question_vote(self, username):
        with transaction.atomic():
            lecture = Lecture.objects.filter(hash='3j7t950').first()
            participant = Participant(username=username, public_nickname=username)
            participant.save()
            lecture.participants.add(participant)
            question = Question(text='How are you?', tags='hello', creator=participant, event=lecture)
            question.save()
            vote = QuestionVote(value=1, voter=participant, question=question)
            vote.save()
            lecture.save()
        return participant, lecture, question

