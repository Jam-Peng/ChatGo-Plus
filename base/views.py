from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import  MyUserCreationForm, UserForm
from .models import User, Room, Message, Friendship
from django.db.models import Q
import uuid


def home(request):
    # rooms = Room.objects.all()
    rooms = Room.objects.filter(is_public = True)
    friends = []

    if request.user.is_authenticated:
        friends = request.user.friends.all()

        # 取得與私人聊天室中最後的訊息
        for friend in friends:
            private_rooms = Room.objects.filter(participants=friend).filter(participants=request.user)
            last_message = Message.objects.filter(room__in=private_rooms).order_by('-created').first()
            # 最後訊息內容
            friend.last_message = last_message
            # 最後訊息時間
            friend.last_message_time = last_message.created if last_message else None

    # 搜尋朋友功能
    q = request.GET.get('q', '')
    if q.strip():
        match_friends = User.objects.filter(
            Q(username__icontains=q) & 
            ~Q(username=request.user.username)    # 排除篩選出自己的帳號
            )
    else:
        match_friends = [] 

    # 新增好友
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        request.user.friends.add(friend)
        return redirect('home')  

    context = {'rooms': rooms, 'friends': friends, 'match_friends': match_friends,}
    return render(request, 'base/index.html', context)


def loginPage(request):
    page = 'login'
    login_message = ''

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = User.objects.filter(username=username)

        if username == "" or password == "":
            login_message = "帳號和密碼不能留空"
        elif not user:
            login_message = "帳號或密碼錯誤"
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
            else:
                login_message = "帳號或密碼錯誤" 

    context = {'page': page, 'login_message': login_message}
    return render(request, 'base/login_register.html', context)


def registerPage(request):
    form = MyUserCreationForm()
    register_message = ''

    if request.method == 'POST':
        username = request.POST.get("username").lower()
        email = request.POST.get("email").lower()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if username == '' or email == '' or password1 == '' or password2 == '':
            register_message = "請正確填寫資料"
        elif password1 != password2:
            register_message = "請確認密碼相同"
        elif User.objects.filter(username = username):
            register_message = "帳號已註冊"
        elif User.objects.filter(email = email):
            register_message = "帳號已註冊"
        else:
            user = User.objects.create_user(
                username = username, 
                email = email, 
                password = password1
            )
            user.save()
            login(request, user)     
            return redirect('home')
    return render(request, 'base/login_register.html', {'form': form, 'register_message': register_message})


# 所有聊天室頁面
def rooms(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(is_public=True).filter(
        Q(host__username__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
    )

    context = {'rooms': rooms, }
    return render(request, 'base/rooms.html', context)


# 建立公開聊天室社群
@login_required(login_url='/login')
def createPublicRoom(request):
    room_uuid = str(uuid.uuid4())

    if request.method == 'POST':
        Room.objects.create(
            host = request.user,
            name = request.POST.get('name'),
            slug = room_uuid,
            description = request.POST.get('description'),
        )
        return redirect('home')
    
    return render(request, 'base/publicRoom_form.html',)


def updatePublicRoom(request, slug):
    room = Room.objects.get(slug=slug) 

    if request.user != room.host:
        return HttpResponse('沒有權限可進行更新')
    
    if request.method == 'POST':
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context = { 'room':room }
    return render(request, 'base/publicRoom_form.html', context)


def deletePublicRoom(request, slug):
    room = Room.objects.get(slug=slug)

    if request.user != room.host:
        return HttpResponse('沒有權限可進行刪除')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': room})


# 參與公開聊天室
@login_required(login_url='/login')
def room(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)
    participants = room.participants.all() 
    
    # ============= sidebar 邏輯 =============  # 
    friends = []
    if request.user.is_authenticated:
        friends = request.user.friends.all()

        # 取得與私人聊天室中最後的訊息
        for friend in friends:
            private_rooms = Room.objects.filter(participants=friend).filter(participants=request.user)
            last_message = Message.objects.filter(room__in=private_rooms).order_by('-created').first()
            # 最後訊息內容
            friend.last_message = last_message
            # 最後訊息時間
            friend.last_message_time = last_message.created if last_message else None

    # 搜尋朋友功能
    q = request.GET.get('q', '')
    if q.strip():
        match_friends = User.objects.filter(
            Q(username__icontains=q) & 
            ~Q(username=request.user.username)    # 排除篩選出自己的帳號
            )
    else:
        match_friends = [] 

    # 新增好友
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        request.user.friends.add(friend)
        return redirect('room', slug=room.slug) 

    context = {'room': room, 'messages': messages, 'participants': participants, 
                'friends': friends, 'match_friends': match_friends,}
    return render(request, 'base/room.html', context)


# 建立私人聊天室的路徑
def createPrivateRoom(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        room_slug = f"{min(request.user.id, friend.id)}-{max(request.user.id, friend.id)}"

        room = Room.objects.filter(slug=room_slug).first()

        if not room:
            # 建立與朋友單一聊天室
            room = Room.objects.create(
                name = friend.name or friend.username, 
                host = request.user,
                slug = room_slug,
                is_public = False,
                )
            room.participants.add(request.user, friend)

        return redirect('private-room', slug=room.slug)
    
    return redirect('home')     # 如果無法切換到私人聊天室頁面，會自動轉回首頁


# 導入好友的私人聊天室
def privateRoom(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)

    friends = []
    if request.user.is_authenticated:
        friends = request.user.friends.all()

    # 搜尋朋友功能
    q = request.GET.get('q', '')
    if q.strip():
        match_friends = User.objects.filter(
            Q(username__icontains=q) & 
            ~Q(username=request.user.username)    # 排除篩選出自己的帳號
            )
    else:
        match_friends = [] 

    # 新增好友
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        request.user.friends.add(friend)
        return redirect('private-room', slug=slug)    
    
    # 取聊天室中最後發訊息的時間
    messages = Message.objects.filter(room=room).order_by('created')  
    last_message_time = None
    if messages.exists() and len(messages) > 0:
        last_message_time = messages[len(messages)-1].created

    context = {'room': room, 'messages': messages, 'last_message_time': last_message_time,
                'friends': friends, 'match_friends': match_friends}
    return render(request, 'base/private_room.html', context)


# 刪除私人聊天室
def deletePrivateRoom(request, slug):
    room = Room.objects.get(slug=slug)

    if request.user != room.host:
        return HttpResponse('沒有權限可進行刪除')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': room})


# 使用者頁面
@login_required(login_url='/login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() 

    friends = []
    if request.user.is_authenticated:
        friends = request.user.friends.all()

        # 取得與私人聊天室中最後的訊息
        for friend in friends:
            private_rooms = Room.objects.filter(participants=friend).filter(participants=request.user)
            last_message = Message.objects.filter(room__in=private_rooms).order_by('-created').first()
            # 最後訊息內容
            friend.last_message = last_message
            # 最後訊息時間
            friend.last_message_time = last_message.created if last_message else None

    # 搜尋朋友功能
    q = request.GET.get('q', '')
    if q.strip():
        match_friends = User.objects.filter(
            Q(username__icontains=q) & 
            ~Q(username=request.user.username)    # 排除篩選出自己的帳號
            )
    else:
        match_friends = [] 

    # 新增好友
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        request.user.friends.add(friend)
        return redirect('user-profile', pk=user.id)  
    
    context = {'user': user, 'rooms': rooms, 'friends': friends, 'match_friends': match_friends}
    return render(request, 'base/profile.html', context)


@login_required(login_url='/login')
def updateUser(request):
    user = request.user                     # 取得當前使用者
    form = UserForm(instance=user)          # 將當前使用者資料加到表單上

    if request.method == 'POST':
        form.name = request.POST.get('name')
        form.username = request.POST.get('username')
        form.email = request.POST.get('email')
        form.bio = request.POST.get('bio')
        form = UserForm(request.POST, request.FILES, instance=user)

        form.save()
        return redirect('user-profile', pk=user.id)
    
    return render(request, 'base/update_user.html', {'form': form, 'user': user})


def deleteFriend(request, pk):
    if not request.user.is_authenticated:
        return HttpResponse('沒有權限可進行刪除')
    
    # 第一種寫法
    friend = User.objects.get(id=pk)
    if request.method == 'POST':
        # 先刪除與好友建立的聊天室
        private_rooms = Room.objects.filter(name=friend)
        for room in private_rooms:
            room.delete()
        # 在刪除好友
        request.user.friends.remove(friend)

        return redirect('home')
    
    # 第二種寫法
    # friend = get_object_or_404(User, id=pk)
    # # 檢查用戶之間是否為朋友，如果是就直接刪除它，不需要經過html直接重新導向首頁
    # friendship = Friendship.objects.filter(from_user=request.user, to_user=friend).first()
    # if friendship:
    #     friendship.delete()
    # return redirect('home')

    return render(request, 'base/delete_user.html', {'obj': friend})
