from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import FriendRequest, ChatMessage, ChatRoom
from django.shortcuts import get_object_or_404
from .decorators import custom_login_required
from django.http import JsonResponse
import uuid
from django.views.decorators.csrf import csrf_exempt

import random
import string

@custom_login_required
def home(request):
    users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)
    sent_requests = FriendRequest.objects.filter(sender=request.user)
    received_requests = FriendRequest.objects.filter(recipient=request.user)
    
    # Create dictionaries to track sent and received requests
    sent_requests_dict = {request.recipient_id: True for request in sent_requests}
    print(sent_requests_dict)
    received_requests_dict = {request.sender_id: True for request in received_requests}
    context = {
        'users': users,
        'sent_requests_dict': sent_requests_dict,
        'received_requests_dict': received_requests_dict
    }
    return render(request, 'index.html', context)






def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        try:
            if request.method == "POST":
                
                username = request.POST['username']
                password = request.POST['password']
                
                user = User.objects.get(username=username)
                
                if user is not None:
                    auth_login(request, user)
                    return redirect('home')
                else:
                    return render(request, 'login.html', {'error_message': 'Invalid username or password.'})
        except Exception as e:
            print(e)
    return render(request, 'login.html')

def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            user = User.objects.create(username=username, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
    return render(request, 'login.html')

def user_logout(request):
    auth_logout(request)
    return redirect('home')

@csrf_exempt
def send_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        if username:
            recipient = User.objects.get(username=username)
            existing_request = FriendRequest.objects.filter(sender=request.user, recipient=recipient).exists()
            if not existing_request:
                FriendRequest.objects.create(sender=request.user, recipient=recipient, status="sent")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Friend request already sent'})
        return JsonResponse({'success': False, 'message': 'Invalid username'})
    
@csrf_exempt
def reject_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        if username:
            to_user = User.objects.get(username=username)
            friend_request = FriendRequest.objects.filter(sender=to_user, recipient=request.user)
            if friend_request.exists():
                friend_request.delete()
                return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    

@csrf_exempt
def accept_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        if username:
            sender = get_object_or_404(User, username=username)
            friend_request = get_object_or_404(FriendRequest, sender=sender, recipient=request.user)
            if friend_request.status == 'sent':
                friend_request.status = 'accepted'
                friend_request.save()

                # Create or retrieve existing ChatRoom
                chat_room, created = ChatRoom.objects.get_or_create(user1=sender, user2=request.user)
                if created:
                    chat_room.room_name = uuid.uuid4().hex[:6]
                    chat_room.save()
                    return JsonResponse({'success': True, 'room_name': chat_room.room_name})
            else:
                return JsonResponse({'success': False, 'message': 'Request could not be accepted.'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid username.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
def chat_room(request, room_name):
    return render(request, 'chat.html', {
        'room_name': room_name
    })
