from channels.generic.websocket import AsyncWebsocketConsumer
import json

from application.models import Question

# group types
private_msg_group_name = 'private_msg_'
question_group_name = 'question_'
approved_question_group_name = 'approved_question_'
all_group_name = 'everyone_'

# msg types:
m_private = "msg_private"
m_question = "msg_question"
m_edit = "msg_edit"
m_delete = "msg_delete"
m_approve = "msg_approve"
m_vote = "msg_vote"
