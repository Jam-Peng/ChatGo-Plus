from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

# 更新使用者的 Form表單模型
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']

