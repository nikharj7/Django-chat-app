from django.db import models
from django.contrib.auth.models import User
import uuid

class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )
    
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.status})"

    def accept(self):
        if self.status == 'sent':
            self.status = 'accepted'
            self.save()
            ChatRoom.objects.create(user1=self.sender, user2=self.recipient)
            return True
        return False

class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, related_name='chat_rooms_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chat_rooms_as_user2', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=100)  # You can generate a unique room name/id here

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"



class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

