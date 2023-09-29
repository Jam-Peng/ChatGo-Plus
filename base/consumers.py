import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message, User
from datetime import datetime
from channels.db import database_sync_to_async


# 序列化函式
def datetime_to_json(obj):
    if isinstance(obj, datetime):
        # return obj.isoformat()              # 格式化 iso
        return obj.strftime('%H:%M')          # 格式化只取時間和分鐘
    raise TypeError("Type not serializable")


# 公開社群聊天室
class ChatConsumer(AsyncWebsocketConsumer):
    # 連接服務器
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 取得當前使用者
        user = self.scope['user']
        if user.is_authenticated:
            await self.add_user_to_room(user, self.room_name)

        await self.accept()
    

    # 使用 database_sync_to_async 將用戶新增到聊天室的模型中
    @database_sync_to_async
    def add_user_to_room(self, user, room_name):
        try:
            room = Room.objects.get(slug=room_name)
            room.participants.add(user)
        except Room.DoesNotExist:
            pass  


    # 斷開服務器 - close_code參數規定必須加上去，不然會出現錯誤提示
    async def disconnect(self, close_code):
        # 取得當前使用者
        user = self.scope['user']
        # 當使者者離開聊天室時 - 如果使用者和聊天室都存在，就移除使用者
        if user is not None and self.room_name is not None:
            await self.remove_user_from_room(user, self.room_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    # 當用戶離開時將用戶從聊天室的模型中移除
    @sync_to_async
    def remove_user_from_room(self, user, room_name):
        try:
            room = Room.objects.get(slug=room_name)
            room.participants.remove(user)
        except Room.DoesNotExist:
            pass 


    # 從 WebSocket 接收發訊者傳出來的訊息
    async def receive(self, text_data):
        data = json.loads(text_data)
        # print(data)

        username = data['username']
        room = data['room']
        message = data['message']
        roomhost = data['roomhost']
        participantsCount = data['participantsCount']


        # 將時間轉換成字串
        messagecreated_str = data['messagecreated'].rstrip('Z')
        messagecreated_format = datetime.fromisoformat(messagecreated_str)
        # 序列化時間格式
        messagecreated_json = datetime_to_json(messagecreated_format)

        # 取得當前登錄的使用者
        user = self.scope['user']
        # 將目前登陸的使用者加到參與者中
        await self.add_user_to_room(user, room)


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
                'roomhost': roomhost.strip(),
                'messagecreated': messagecreated_json,
                'participantsCount': participantsCount
            }
        )


    # 從聊天室的群組中接收訊息
    async def chat_message(self, event):
        username = event['username']
        room = event['room']
        message = event['message']
        roomhost = event['roomhost']
        messagecreated = event['messagecreated']
        participantsCount = event['participantsCount']
        

        # 傳送訊息到 WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'room': room,
            'message': message,
            'roomhost': roomhost,
            'messagecreated': messagecreated,
            'participantsCount': participantsCount,
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


# 私人聊天室
class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"private_{self.room_name}"

        # 加入私人聊天室
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 離開私人聊天室
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        username = data['username']
        room = data['room']
        message = data['message']
        roomhost = data['roomhost']

        # 將時間轉換成字串
        messagecreated_str = data['messagecreated'].rstrip('Z')
        messagecreated_format = datetime.fromisoformat(messagecreated_str)
        # 序列化時間格式
        messagecreated_json = datetime_to_json(messagecreated_format)

        # 將發訊者傳出的資料傳到資料庫(再傳到群組聊天室給其他參與者前)
        await self.save_message(username, room, message, )

        # 將私人訊息傳送到私人聊天室中
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'room': room,
                'message': message,
                'roomhost': roomhost.strip(),
                'messagecreated': messagecreated_json
            }
        )

    # 從聊天室的群組中接收訊息
    async def chat_message(self, event):
        username = event['username']
        room = event['room']
        message = event['message']
        roomhost = event['roomhost']
        messagecreated = event['messagecreated']

        # 傳送訊息到 WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'room': room,
            'message': message,
            'roomhost': roomhost,
            'messagecreated': messagecreated,
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

