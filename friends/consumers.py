from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from friends.models import FriendRequest, FriendList, Notification, Thread, Message


# code
class NotifyDB:
    '''friend request API'''
    def __init__(self):
        pass

    @database_sync_to_async
    def create(self, receiver, sender, message, category):
        notification, created = Notification.get_or_create(
            receiver=receiver, sender=sender, message=message, category=category
        )
        return notification
    
    @database_sync_to_async
    def check(self, user):
        pass

notify = NotifyDB()


class NotificationConsumer(AsyncJsonWebsocketConsumer):

    # connect
    async def connect(self):
        # 
        self.user = self.scope['user']
        # 
        if self.user.is_authenticated:
            self.group_name = f"Notifications_{self.user.username}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    # receive json
    async def receive_json(self, data):
        await self.channel_layer.group_send(self.group_name, {
            'type': data['category'], 
            'payload': data['payload'],
        })

    # sending request
    async def send_request(self, data):
        category = data['type']
        payload = data['payload']
        # 
        sender = self.user.username
        receiver = payload['receiver']
        message = payload['message']
        await notify.create(receiver, sender, message, category=category)
        # 
        await self.channel_layer.group_send(f"Notifications_{receiver}", {
            'type': "proceed_" + category,
            'payload': {
                'category': category,
                'sender': sender,
                'message': message
            }
        })

    async def proceed_send_request(self, data):
        await self.send_json(data['payload'])

    # receiving request
    async def receive_request(self, data):
        category = data['type']
        payload = data['payload']
        # 
        sender = self.user.username
        accepted = payload['accepted']
        receiver = payload['receiver']
        message = payload['message']
        await notify.create(receiver, sender, message, category=category)
        # 
        await self.channel_layer.group_send(f"Notifications_{receiver}", {
            'type': "proceed_" + category,
            'payload': {
                'category': category,
                'sender': sender,
                'message': message,
                'accepted': accepted
            }
        })

    async def proceed_receive_request(self, data):
        await self.send_json(data['payload'])

    # disconnect
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)



''' chatting '''

class ThreadAPI:

    @database_sync_to_async
    def save(self, username1, username2):
        thread, created = Thread.get_or_create(username1, username2)
        return thread

class MessageAPI:

    @database_sync_to_async
    def save(self, text, thread_name, user):
        return Message.create(text, thread_name, user)

class PersonalChatConsumer(AsyncJsonWebsocketConsumer):

    # connecting
    async def connect(self):
        # 
        self.user = self.scope['user'] 
        my_username = self.user.username
        other_username = self.scope['url_route']['kwargs']['username']
        self.group_name = Thread.name(my_username, other_username)
        if not self.user.is_authenticated: 
            print("seee")
            return
        #
        await ThreadAPI.save(my_username, other_username)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    # receiving
    async def receive_json(self, data):
        await MessageAPI.save(
            data["message"], self.group_name, self.user
        )
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat.message", 
            "message": {
                "text": data["message"], 
                "user": self.user.username
            }
        })

    # sending
    async def chat_message(self, event):
        await self.send_json(event["message"])

    # disconnecting
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
