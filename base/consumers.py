import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message, User


class ChatConsumer(AsyncWebsocketConsumer):
    # 連接服務器
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    # 斷開服務器 - close_code參數規定必須加上去，不然會出現錯誤提示
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 從 WebSocket 接收發訊者傳出來的訊息
    async def receive(self, text_data):
        data = json.loads(text_data)
        # print(data)

        username = data['username']
        room = data['room']
        message = data['message']
        roomhost = data['roomhost']

        # 將發訊者傳出的資料傳到資料庫(再傳到群組聊天室給其他參與者前)
        await self.save_message(username, room, message, )

        # 將訊息傳送到聊天室群組中
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'room': room,
                'message': message,
                'roomhost':roomhost.strip(),
            }
        )


    # 從聊天室的群組中接收訊息
    async def chat_message(self, event):
        username = event['username']
        room = event['room']
        message = event['message']
        roomhost = event['roomhost']

        # 傳送訊息到 WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'room': room,
            'message': message,
            'roomhost': roomhost,
        }))

    # 處理與資料庫資料的 CRUD
    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)

        # 取得目前訊息總數控制在一定數量的訊息
        messages = Message.objects.filter(room=room)
        # print(messages[:10])
        if messages.count() > 20:
            # 先依照建立的時間找到需要删除的訊息id，在篩選出這些訊息執行刪除
            messages_to_delete = messages.order_by('created')[:10].values_list('id', flat=True)
            Message.objects.filter(id__in=messages_to_delete).delete()
            
        Message.objects.create(user=user, room=room, content=message)