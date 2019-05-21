from application.models import Lecture
from .common import *


class ModeratorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
        if not Lecture.objects.filter(hash=self.lecture_name) \
                or Lecture.objects.filter(hash=self.lecture_name).first().closed:
            raise ValueError('Unknown lecture id.')
        self.approved_msg_gn = approved_question_group_name + self.lecture_name
        self.question_msg_gn = question_group_name + self.lecture_name
        self.all_msg_gn = all_group_name + self.lecture_name

        # Join room group
        await self.channel_layer.group_add(
            self.approved_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.question_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.all_msg_gn,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.approved_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.question_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.all_msg_gn,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json['type'] == m_edit:
            pass
        elif text_data_json['type'] == m_delete:

            await self.channel_layer.group_send(
                self.question_msg_gn,
                {
                    'type': m_delete,
                    'question_id': text_data_json['question_id']
                }
            )

        elif text_data_json['type'] == m_approve:

            question_id = text_data_json['question_id']
            lecture = Lecture.objects.filter(hash=self.lecture_name).first()
            question = Question.objects.filter(pk=question_id)
            if not question:
                raise ValueError('Bad question id')
            if question.first().event != lecture:
                raise RuntimeError('Question is not assigned to given lecture')


            question = question.first()
            question.approved = True
            question.save()

            await self.channel_layer.group_send(
                self.approved_msg_gn,
                {
                    'type': m_approve,
                    'question_id': text_data_json['question_id'],
                    'question': question.text,
                    'tags': question.tags,
                }
            )

        else:
            raise ValueError("UserConsumer: no handler for message type {0}!".format(text_data_json['type']))

    async def msg_question(self, event):
        question = event['question']
        tags = event['tags']
        event['type'] = m_question
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
