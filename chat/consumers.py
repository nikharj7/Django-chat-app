import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import FriendRequest, ChatMessage
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.room_name = f'user_{self.user.id}'
            # Join room group
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            user_id = data.get('user_id')

            if action == 'send_request':
                await self.send_request(user_id)
            elif action == 'reject_request':
                await self.reject_request(user_id)
            elif action == 'accept_request':
                await self.accept_request(user_id)
            elif action == 'send_message':
                message = data.get('message')
                recipient_id = data.get('recipient_id')
                await self.send_message(message, recipient_id)
            elif action == 'exit_chat':
                await self.exit_chat()

        except Exception as e:
            print(f"Error in receive method: {e}")

    async def send_request(self, user_id):
        recipient = await sync_to_async(User.objects.get)(id=user_id)
        existing_request = await sync_to_async(FriendRequest.objects.filter(sender=self.user, recipient=recipient).exists)()
        if not existing_request:
            await sync_to_async(FriendRequest.objects.create)(sender=self.user, recipient=recipient)
            await self.channel_layer.group_send(
                f'user_{user_id}',
                {
                    'type': 'request_received',
                    'user_id': self.user.id
                }
            )
            await self.send(text_data=json.dumps({
                'action': 'request_sent',
                'user_id': user_id
            }))

    async def reject_request(self, user_id):
        sender = await sync_to_async(User.objects.get)(id=user_id)
        friend_request = await sync_to_async(FriendRequest.objects.filter(sender=sender, recipient=self.user).first)()
        if friend_request:
            await sync_to_async(friend_request.delete)()
            await self.channel_layer.group_send(
                f'user_{user_id}',
                {
                    'type': 'request_rejected',
                    'user_id': self.user.id
                }
            )
            await self.send(text_data=json.dumps({
                'action': 'request_rejected',
                'user_id': user_id
            }))

    async def accept_request(self, user_id):
        sender = await sync_to_async(User.objects.get)(id=user_id)
        friend_request = await sync_to_async(FriendRequest.objects.filter(sender=sender, recipient=self.user).first)()
        if friend_request:
            await sync_to_async(friend_request.delete)()

            # Notify both users to open the chat window
            await self.channel_layer.group_send(
                f'user_{self.user.id}',
                {
                    'type': 'request_accepted',
                    'user_id': sender.id
                }
            )
            await self.channel_layer.group_send(
                f'user_{sender.id}',
                {
                    'type': 'request_accepted',
                    'user_id': self.user.id
                }
            )

            # Send response to the sender for redirection
            await self.send(text_data=json.dumps({
                'action': 'request_accepted',
                'user_id': user_id
            }))


    async def send_message(self, message, recipient_id):
        recipient = await sync_to_async(User.objects.get)(id=recipient_id)
        chat_message = await sync_to_async(ChatMessage.objects.create)(
            sender=self.user,
            recipient=recipient,
            message=message
        )
        await self.channel_layer.group_send(
            f'user_{recipient_id}',
            {
                'type': 'chat_message',
                'message': chat_message.message,
                'sender': self.user.username
            }
        )
        await self.send(text_data=json.dumps({
            'action': 'chat_message',
            'message': chat_message.message,
            'sender': self.user.username
        }))

    async def request_received(self, event):
        user_id = event['user_id']
        await self.send(text_data=json.dumps({
            'action': 'request_received',
            'user_id': user_id
        }))

    async def request_rejected(self, event):
        user_id = event['user_id']
        await self.send(text_data=json.dumps({
            'action': 'request_rejected',
            'user_id': user_id
        }))

    async def request_accepted(self, event):
        user_id = event['user_id']
        await self.send(text_data=json.dumps({
            'action': 'request_accepted',
            'user_id': user_id
        }))

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'action': 'chat_message',
            'message': message,
            'sender': sender
        }))

    async def exit_chat(self):
        # Notify both users to exit chat
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_closed',
                'user_id': self.user.id
            }
        )

    async def chat_closed(self, event):
        # Send message to close chat for the current user
        await self.send(text_data=json.dumps({
            'action': 'chat_closed'
        }))
        # Close WebSocket connection
        await self.close()
