from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views, consumers

# Set up the router for API views
router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'messages', views.ChatMessageViewSet, basename='chatmessage')
router.register(r'staff', views.SupportStaffViewSet, basename='supportstaff')

# URL patterns
urlpatterns = [
    # Template views
    path('', views.chat_home, name='chat_home'),
    path('room/<str:room_id>/', views.chat_room, name='chat_room'),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # WebSocket endpoint - Django won't handle this directly, but it helps with URL resolution
    re_path(r'ws/chat/(?P<room_id>\w+)/$', views.websocket_view, name='ws_chat'),
] 