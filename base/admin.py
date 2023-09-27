from django.contrib import admin
from .models import Room, Message, User, Friendship

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(User)
admin.site.register(Friendship)
