from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from base64 import b64decode, b64encode

from .models import Message
from .shared.ldap import Server
from .shared.utils import encrypt_from_pem_crt, Rsa_Service

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        user = User.objects.filter(username=self.scope['user'].login)[0]
        # print('-----------------------')
        # print(user.pk)
        # print('-----------------------')
        messages = Message.last_10_messages(user.pk)
        content = {
            'command': 'messages',
            'type': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        recipient = data['to']
        author = self.scope['user'].login

        # plain_message = Rsa_Service.decrypt(b64decode(data['message'].encode()))
        plain_message = data['message']

        author_user = Server.ldap_server.find_client(author)
        recipient_user = Server.ldap_server.find_client(recipient)
        author_user_1 = User.objects.filter(username=author)[0]
        recipient_user_1 = User.objects.filter(username=recipient)[0]

        message = Message.objects.create(
            author=author_user_1,
            recipient=recipient_user_1,
            content=data['message'])
        content = {
            'command': 'new_message',
            'to': recipient,
            'from': author,
            'message': plain_message
        }
        return self.send_chat_message(content, recipient_user.certification, author_user.certification)

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

    def send_chat_message(self, message, to_pen_crt, from_pen_crt):
        async_to_sync(self.channel_layer.group_send)(
            'chat_%s' % message['from'],
            {
                'type': 'chat_message',
                'cipherMessage': b64encode(encrypt_from_pem_crt(
                    # self.scope['user_certificate'].encode(),
                    from_pen_crt.encode(),
                    message=message['message'].encode()
                )).decode(),
            }
        )
        async_to_sync(self.channel_layer.group_send)(
            'chat_%s' % message['to'],
            {
                'type': 'chat_message',
                'cipherMessage': b64encode(encrypt_from_pem_crt(
                    to_pen_crt.encode(),
                    message=message['message'].encode()
                )).decode(),
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
        print(event)
        # message = event['cipherMessage']
        self.send(text_data=json.dumps(event))
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
