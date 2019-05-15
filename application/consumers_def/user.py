from .common import *


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_name = self.scope['url_route']['kwargs']['lecture_name']
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

            # persist message
            # Question.

            # Send message to room group
            await self.channel_layer.group_send(
                self.question_msg_gn,
                {
                    'type': m_question,
                    'question': question,
                    'tags': tags
                }
            )
        elif text_data_json['type'] == m_private:
            title = text_data_json['title']
            text = text_data_json['text']

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
            await self.channel_layer.group_send(
                self.question_msg_gn,
                {
                    'type': m_vote,
                    'question_id': question_id
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
