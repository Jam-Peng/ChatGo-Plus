from django.db import models
from django.contrib.auth.models import AbstractUser


# 擴充自定義使用(管理)者模型
class User(AbstractUser):
    name = models.CharField(max_length=200, default="None", null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    friends = models.ManyToManyField("self", through='Friendship', symmetrical=False)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default='avatar.png')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class Friendship(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_friend_set')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_friend_set')
    chat_count = models.PositiveIntegerField(default=0)     # 聊天次數
    created = models.DateTimeField(auto_now_add=True)       
    updated = models.DateTimeField(auto_now=True)          

    class Meta:
        unique_together = ['from_user', 'to_user']
        ordering = ['-updated', '-chat_count']           

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    is_public = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.name)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['updated', 'created']  
    
    def __str__(self):
        return self.content[:50]  
    