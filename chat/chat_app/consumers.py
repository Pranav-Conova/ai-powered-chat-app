import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from .topic_manager import current_topic, add_message, get_chat_history

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_topic'
        self.user_id = str(uuid.uuid4())

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send current topic and user_id
        await self.send(text_data=json.dumps({
            'type': 'system',
            'topic': f"{current_topic}",
            'user_id': self.user_id
        }))

        # Send chat history
        for item in get_chat_history():
            await self.send(text_data=json.dumps({
                'message': item["message"],
                'user_id': item["user_id"]
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Save message to history
        add_message(message, self.user_id)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_id': event['user_id']
        }))

    async def send_new_topic(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system',
            'topic': event["message"]
        }))
