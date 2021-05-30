from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message
from .shared.utils import encrypt_from_pem_crt, Rsa_Service

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        messages = Message.last_10_messages()
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        recipient = data['to']
        author = self.scope['user'].login

        author_user = User.objects.filter(username=author)[0]
        recipient_user = User.objects.filter(username=recipient)[0]

        message = Message.objects.create(
            author=author_user,
            recipient=recipient_user,
            content=data['message'])
        content = {
            'command': 'new_message',
            'to': recipient,
            'from': author,
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.login,
            'recipient': message.recipient.login,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['user'].login
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(Rsa_Service.get_certificate())

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        recipient_user = User.objects.filter(username=message['to'])[0]
        to_pen_crt = recipient_user.certificate
        to_message = json.dumps({
            'type': 'chat_message',
            'message': message,
        })
        from_message = json.dumps({
            'type': 'chat_message',
            'message': message
        })
        async_to_sync(self.channel_layer.group_send)(
            message['from'],
            {
                'cipherMessage': encrypt_from_pem_crt(
                    self.scope['user_certificate'].encode(),
                    message=from_message
                ),
            }
        )
        async_to_sync(self.channel_layer.group_send)(
            message['to'],
            {
                'cipherMessage': encrypt_from_pem_crt(
                    to_pen_crt.encode(),
                    message=to_message
                ),
            }
        )

    def send_message(self, message):
        # async_to_sync(self.channel_layer.group_send)(
        #     'self.channel_name',
        #     {
        #         'type': 'chat_message',
        #         'message': 'e'
        #     }
        # )
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
# import json
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer
#
#
# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.user_login = self.scope['user'].login
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         self.accept()
#
#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     def chat_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'message': message
#         }))
