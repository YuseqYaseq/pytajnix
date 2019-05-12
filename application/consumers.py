# application/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from application.models import Question


class LecturerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
        self.lecture_group_name = 'lecture_%s' % self.lecture_name

        # Join room group
        await self.channel_layer.group_add(
            self.lecture_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.lecture_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'question_msg':
            question = text_data_json['question']
            tags = text_data_json['tags']

            # persist message
            # Question.

            # Send message to room group
            await self.channel_layer.group_send(
                self.lecture_group_name,
                {
                    'type': 'question_msg',
                    'question': question,
                    'tags': tags
                }
            )
        else:
            title = text_data_json['title']
            text = text_data_json['text']

            # Send message to room group
            await self.channel_layer.group_send(
                self.lecture_group_name,
                {
                    'type': 'direct_msg',
                    'title': title,
                    'text': text
                }
            )

    # Receive question from audience
    async def question_msg(self, event):
        question = event['question']
        tags = event['tags']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'question_msg',
            'question': question,
            'tags': tags
        }))

    # Receive direct message from audience
    async def direct_msg(self, event):
        title = event['title']
        text = event['text']

        await self.send(text_data=json.dumps({
            'type': 'direct_msg',
            'title': title,
            'text': text,
        }))

class ModeratorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, data):
        pass


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
        self.lecture_group_name = 'lecture_%s' % self.lecture_name

        # Join room group
        await self.channel_layer.group_add(
            self.lecture_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.lecture_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'question_msg':
            question = text_data_json['question']
            tags = text_data_json['tags']

            # persist message
            # Question.

            # Send message to room group
            await self.channel_layer.group_send(
                self.lecture_group_name,
                {
                    'type': 'question_msg',
                    'question': question,
                    'tags': tags
                }
            )
        else:
            title = text_data_json['title']
            text = text_data_json['text']

            # Send message to room group
            await self.channel_layer.group_send(
                self.lecture_group_name,
                {
                    'type': 'direct_msg',
                    'title': title,
                    'text': text
                }
            )

    # Receive question from audience
    async def question_msg(self, event):
        question = event['question']
        tags = event['tags']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'question_msg',
            'question': question,
            'tags': tags
        }))

    # Receive direct message from audience
    async def direct_msg(self, event):
        title = event['title']
        text = event['text']

        await self.send(text_data=json.dumps({
            'type': 'direct_msg',
            'title': title,
            'text': text,
        }))
