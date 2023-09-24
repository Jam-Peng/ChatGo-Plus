from django.shortcuts import render, redirect
from .forms import  MyUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User


def home(request):

    context = {}
    return render(request, 'chat/index.html', context)


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
    return render(request, 'chat/login_register.html', context)


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
        else:
            user = User.objects.create_user(
                username = username, 
                email = email, 
                password = password1
            )
            user.save()
            login(request, user)     
            return redirect('home')
    return render(request, 'chat/login_register.html', {'form': form, 'register_message': register_message})


def logoutUser(request):
    logout(request)
    return redirect('home')

