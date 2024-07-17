from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    # path('chat/<int:user_id>/', views.chat, name='chat')
    path('login', views.user_login, name="login"),
    path('register', views.user_register, name="register"),
    path('logout', views.user_logout, name="logout"),
    path('send_request', views.send_request, name="send_request"),
    path('reject_request', views.reject_request, name='reject_request'),
    path('accept_request', views.accept_request, name='accept_request'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)