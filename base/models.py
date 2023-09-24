from django.db import models
from django.contrib.auth.models import AbstractUser


# 擴充自定義使用(管理)者模型
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    # avatar = models.ImageField(null=True, default='avatar.svg')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return str(self.name)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_added']
    
    def __str__(self):
        return self.content[:50]  
    