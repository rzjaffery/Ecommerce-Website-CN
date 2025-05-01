import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import ChatRoom, ChatMessage
import jwt
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Get the token from the query string and authenticate
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if not token:
            # No token provided, reject the connection
            await self.close()
            return
        
        try:
            # Verify the JWT token
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user_id = payload[settings.SIMPLE_JWT['USER_ID_CLAIM']]
            self.user = await self.get_user(user_id)
            
            # Check if user has access to this room
            has_access = await self.check_room_access(self.user, self.room_id)
            if not has_access:
                await self.close()
                return
            
            # Add the user to the room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Notify other users that this user has joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timezone.now().isoformat(),
                }
            )
            
        except jwt.PyJWTError:
            # Invalid token, reject the connection
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave the room group
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Notify other users that this user has left
            if hasattr(self, 'user'):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_leave',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'timestamp': timezone.now().isoformat(),
                    }
                )
        except:
            pass
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            
            # Save the message to the database
            chat_message = await self.save_message(
                room_id=self.room_id,
                user=self.user,
                message=message
            )
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': chat_message['timestamp'],
                    'message_id': chat_message['id']
                }
            )
        elif message_type == 'typing':
            # Send typing notification to room group
            is_typing = text_data_json.get('is_typing', False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': is_typing
                }
            )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    async def user_join(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def user_leave(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def user_typing(self, event):
        # Send typing notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def check_room_access(self, user, room_id):
        try:
            room = ChatRoom.objects.get(room_id=room_id)
            # Check if user is the room creator, the support staff, or a support staff for an unassigned room
            return (user == room.user or 
                   user == room.support_staff or 
                   (hasattr(user, 'support_profile') and room.support_staff is None))
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, room_id, user, message):
        # Get the room
        room = ChatRoom.objects.get(room_id=room_id)
        
        # Update room timestamp
        room.updated_at = timezone.now()
        room.save()
        
        # Create the message
        chat_message = ChatMessage.objects.create(
            room=room,
            sender=user,
            message=message
        )
        
        return {
            'id': chat_message.id,
            'timestamp': chat_message.timestamp.isoformat()
        } 