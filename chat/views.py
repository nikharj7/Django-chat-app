from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import FriendRequest, ChatMessage
from django.shortcuts import get_object_or_404
from .decorators import custom_login_required
import random
import string

@custom_login_required
def home(request):
    users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)
    sent_requests = FriendRequest.objects.filter(sender=request.user)
    received_requests = FriendRequest.objects.filter(recipient=request.user)

    sent_requests_dict = {request.recipient_id: True for request in sent_requests}
    received_requests_dict = {request.sender_id: True for request in received_requests}

    context = {
        'users': users,
        'sent_requests_dict': sent_requests_dict,
        'received_requests_dict': received_requests_dict
    }
    return render(request, 'index.html', context)



@custom_login_required
def chat(request, user_id):
    # Retrieve the other user based on user_id
    other_user = get_object_or_404(User, id=user_id)
    
    # Generate a random unique ID for the chat room
    room_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
    # Query chat messages between current user and the other user
    messages = ChatMessage.objects.filter(
        sender__in=[request.user, other_user],
        recipient__in=[request.user, other_user]
    )
    
    context = {
        'other_user': other_user,
        'messages': messages,
        'room_id': room_id  # Pass room_id to the template
    }
    
    return render(request, 'chat.html', context)



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