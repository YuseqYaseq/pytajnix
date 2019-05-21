from application.models import Lecture
from .common import *


class LecturerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
        if not Lecture.objects.filter(hash=self.lecture_name) \
                or Lecture.objects.filter(hash=self.lecture_name).first().closed:
            raise ValueError('Unknown lecture id.')
        self.private_msg_gn = private_msg_group_name + self.lecture_name
        self.approved_question_gn = approved_question_group_name + self.lecture_name
        self.all_msg_gn = all_group_name + self.lecture_name

        self.sent_questions = []

        # Join room group
        await self.channel_layer.group_add(
            self.private_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.approved_question_gn,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.all_msg_gn,
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
            self.approved_question_gn,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.all_msg_gn,
            self.channel_name
        )

    # Receive from websocket
    async def receive(self, text_data):
        pass

    # Receive approved question
    async def msg_approve(self, event):
        question = event['question']
        tags = event['tags']
        question_id = event['question_id']
        self.sent_questions.append(question_id)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': m_approve,
            'question': question,
            'question_id': question_id,
            'tags': tags
        }))

    # Receive private message
    async def msg_private(self, event):
        await self.send(text_data=json.dumps(event))

    # Receive question (when moderation is turned off)
    async def msg_question(self, event):
        question = event['question']
        tags = event['tags']
        question_id = event['question_id']
        self.sent_questions.append(question_id)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': m_question,
            'question': question,
            'question_id': question_id,
            'tags': tags
        }))

    async def msg_vote(self, event):
        question_id = event['question_id']
        if question_id not in self.sent_questions:
            return
        await self.send(text_data=json.dumps(event))
