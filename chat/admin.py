from django.contrib import admin
from .models import FriendRequest, ChatMessage
# Register your models here.


admin.site.register(FriendRequest)
admin.site.register(ChatMessage)