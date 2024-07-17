from django.contrib import admin
from .models import FriendRequest, ChatMessage, ChatRoom
# Register your models here.


admin.site.register(FriendRequest)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)