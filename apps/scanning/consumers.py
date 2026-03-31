import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ScanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.region_name = self.scope['url_route']['kwargs'].get('region_name', 'dashboard')
        self.room_group_name = f'scan_{self.region_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add('scan_dashboard', self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to scan feed: {self.region_name}',
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard('scan_dashboard', self.channel_name)

    async def scan_update(self, event):
        await self.send(text_data=json.dumps(event['data']))