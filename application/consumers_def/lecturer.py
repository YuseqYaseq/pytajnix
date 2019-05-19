from application.models import Lecture
from .common import *


class LecturerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
        if not Lecture.objects.filter(hash=self.lecture_name):
            raise ValueError('Unknown lecture id.')
        self.private_msg_gn = private_msg_group_name + self.lecture_name
        self.approved_question_gn = approved_question_group_name + self.lecture_name

        # Join room group
        await self.channel_layer.group_add(
            self.private_msg_gn,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.approved_question_gn,
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

    # Receive from websocket
    async def receive(self, text_data):
        pass

    # Receive approved question
    async def msg_approve(self, event):
        question = event['question']
        tags = event['tags']
        question_id = event['question_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': m_approve,
            'question': question,
            'question_id': question_id,
            'tags': tags
        }))

    # Receive private message
    async def msg_private(self, event):
        title = event['title']
        text = event['text']
        print("dupa1")
        await self.send(text_data=json.dumps({
            'type': m_private,
            'title': title,
            'text': text,
        }))
