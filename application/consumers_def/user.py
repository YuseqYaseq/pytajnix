from django.contrib.auth.models import User

from application.models import Lecture, DirectMessage
from .common import *
from django.utils import timezone


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
        if not Lecture.objects.filter(hash=self.lecture_name):
            raise ValueError('Unknown lecture id.')
        self.private_msg_gn = private_msg_group_name + self.lecture_name
        self.question_msg_gn = question_group_name + self.lecture_name

        # Join room group
        await self.channel_layer.group_add(
            self.private_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.question_msg_gn,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.private_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.question_msg_gn,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == m_question:
            question = text_data_json['question']
            tags = text_data_json['tags']
            creator = text_data_json['creator']

            # persist message
            lecture = Lecture.objects.filter(hash=self.lecture_name).first()
            creator_entity = User.objects.filter(username=creator)
            if not creator_entity:
                raise ValueError('Unknown user')
            creator_entity = creator_entity.first()
            question_entity = Question()
            question_entity.text = question
            question_entity.approved = not lecture.moderated
            question_entity.creator = creator_entity
            question_entity.event = lecture
            question_entity.save()
            # Send message to room group
            await self.channel_layer.group_send(
                self.question_msg_gn,
                {
                    'type': m_question,
                    'question': question,
                    'tags': tags,
                    'question_id': question_entity.pk
                }
            )
        elif text_data_json['type'] == m_private:
            title = text_data_json['title']
            text = text_data_json['text']
            creator = text_data_json['creator']
            lecture = Lecture.objects.filter(hash=self.lecture_name).first()
            creator_entity = User.objects.filter(username=creator)
            if not creator_entity:
                raise ValueError('Unknown user')
            creator_entity = creator_entity.first()
            if lecture.directmessages_receiver:
                receiver = lecture.lecturer_lectures.first()
            else:
                receiver = None
            message = DirectMessage()
            message.event = lecture
            message.creator = creator_entity
            message.title = title
            message.text = text
            message.date_time = timezone.now()
            message.receiver = receiver
            message.save()

            # Send message to room group
            await self.channel_layer.group_send(
                self.private_msg_gn,
                {
                    'type': m_private,
                    'title': title,
                    'text': text
                }
            )
        elif text_data_json['type'] == m_vote:
            question_id = text_data_json['question_id']
            creator = text_data_json['creator']
            vote_value = int(text_data_json['vote'])
            if vote_value != -1 and vote_value != 1:
                raise ValueError('Bad vote value.')
            creator_entity = User.objects.filter(username=creator)
            if not creator_entity:
                raise ValueError('Unknown user')
            creator_entity = creator_entity.first()
            lecture = Lecture.objects.filter(hash=self.lecture_name).first()
            question = Question.objects.filter(pk=question_id)
            if question not in lecture.question_set:
                raise RuntimeError('Question is not assigned to given lecture')
            if not question:
                raise ValueError('Bad question id')
            question = question.first()
            if not question.can_vote(creator_entity):
                raise RuntimeError('User cannot vote on this question.')
            question.add_vote(creator_entity, vote_value)
            question.save()

            await self.channel_layer.group_send(
                self.question_msg_gn,
                {
                    'type': m_vote,
                    'question_id': question_id,
                    'vote': vote_value
                }
            )
        else:
            raise ValueError("UserConsumer: no handler for message type {0}!".format(text_data_json['type']))

    async def msg_private(self, event):
        title = event['title']
        text = event['text']

        await self.send(text_data=json.dumps({
            'type': 'direct_msg',
            'title': title,
            'text': text,
        }))

    # Receive question from audience
    async def msg_question(self, event):
        question = event['question']
        tags = event['tags']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': m_question,
            'question': question,
            'tags': tags
        }))

    async def msg_edit(self, event):
        event['type'] = m_edit
        await self.send(text_data=json.dumps(event))

    async def msg_delete(self, event):
        event['type'] = m_delete
        await self.send(text_data=json.dumps(event))

    async def msg_approve(self, event):
        event['type'] = m_approve
        await self.send(text_data=json.dumps(event))

    async def msg_vote(self, event):
        event['type'] = m_vote
        await self.send(text_data=json.dumps(event))
