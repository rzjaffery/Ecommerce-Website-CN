from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone
import uuid
import logging
from django.core.cache import cache
from django.conf import settings

# REST Framework imports
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# JWT Token imports
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# Models and serializers
from .models import ChatRoom, ChatMessage, SupportStaff
from .serializers import (
    ChatRoomSerializer, 
    ChatRoomWithMessagesSerializer,
    ChatMessageSerializer, 
    SupportStaffSerializer,
    UserSerializer
)

# Set up logging
logger = logging.getLogger('django.channels')

# Cache time in seconds
CACHE_TTL = getattr(settings, 'CACHE_TIMEOUT', 900)  # 15 minutes default

# Generate tokens for WebSocket authentication
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Template Views
@login_required
def chat_home(request):
    """
    Main chat interface for users
    """
    # For support staff, show all active chats
    if hasattr(request.user, 'support_profile'):
        chat_rooms = ChatRoom.objects.filter(
            Q(support_staff=request.user) | Q(support_staff__isnull=True),
            is_active=True
        ).order_by('-updated_at')
    else:
        # For regular users, show only their chats
        chat_rooms = ChatRoom.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-updated_at')
    
    # Get or create support staff profile if user is staff
    if request.user.is_staff and not hasattr(request.user, 'support_profile'):
        SupportStaff.objects.create(user=request.user)
    
    # Generate JWT token for WebSocket authentication
    tokens = get_tokens_for_user(request.user)
    
    context = {
        'chat_rooms': chat_rooms,
        'is_support': hasattr(request.user, 'support_profile'),
        'ws_token': tokens['access'],
    }
    return render(request, 'chat/chat_home.html', context)

@login_required
def chat_room(request, room_id):
    """
    Chat room detail view
    """
    room = get_object_or_404(ChatRoom, room_id=room_id)
    
    # Check if user is authorized to view this room
    if not (request.user == room.user or request.user == room.support_staff or 
            (hasattr(request.user, 'support_profile') and room.support_staff is None)):
        return render(request, 'chat/access_denied.html')
    
    # Assign support staff if not assigned and current user is support
    if hasattr(request.user, 'support_profile') and room.support_staff is None:
        room.support_staff = request.user
        room.save()
    
    # Mark messages as read
    ChatMessage.objects.filter(
        room=room,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    # Get messages
    messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
    
    # Generate JWT token for WebSocket authentication
    tokens = get_tokens_for_user(request.user)
    
    context = {
        'room': room,
        'messages': messages,
        'is_support': hasattr(request.user, 'support_profile'),
        'ws_token': tokens['access'],
    }
    return render(request, 'chat/chat_room.html', context)

def websocket_view(request, room_id):
    """
    Dummy view for WebSocket connections - actual handling is done by ASGI/Channels
    This is just for URL resolution purposes.
    """
    logger.debug(f"WebSocket view called for room: {room_id}")
    return HttpResponse("WebSocket endpoint - Connect using WebSocket protocol, not HTTP.")

# API Views
class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat rooms
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'room_id'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRoomWithMessagesSerializer
        return ChatRoomSerializer
    
    def get_queryset(self):
        user = self.request.user
        cache_key = f'chat_rooms:{user.id}:{user.is_staff}'
        
        # Try to get from cache first
        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset
            
        # If not in cache, fetch from database
        if hasattr(user, 'support_profile'):
            # Support staff can see all active rooms and rooms assigned to them
            queryset = ChatRoom.objects.filter(
                Q(support_staff=user) | Q(support_staff__isnull=True),
                is_active=True
            ).order_by('-updated_at')
        else:
            # Regular users can only see their own rooms
            queryset = ChatRoom.objects.filter(
                user=user,
                is_active=True
            ).order_by('-updated_at')
            
        # Store in cache for future requests
        cache.set(cache_key, queryset, CACHE_TTL // 2)  # Shorter TTL for dynamic data
        return queryset
    
    def perform_create(self, serializer):
        # Generate a unique room ID and assign the current user
        room_id = str(uuid.uuid4())[:8]
        serializer.save(user=self.request.user, room_id=room_id)
    
    @action(detail=True, methods=['post'])
    def close(self, request, room_id=None):
        """
        Close a chat room
        """
        room = self.get_object()
        room.is_active = False
        room.save()
        return Response({'status': 'chat closed'})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, room_id=None):
        """
        Assign a support staff to a chat room
        """
        if not hasattr(request.user, 'support_profile'):
            return Response(
                {'error': 'Only support staff can be assigned to rooms'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        room = self.get_object()
        if room.support_staff and room.support_staff != request.user:
            return Response(
                {'error': 'Room already has an assigned support staff'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room.support_staff = request.user
        room.save()
        return Response({'status': 'assigned to room'})

class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat messages
    """
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Filter messages based on user's role
        if hasattr(user, 'support_profile'):
            # Support staff can see messages in rooms they're assigned to or unassigned
            return ChatMessage.objects.filter(
                Q(room__support_staff=user) | 
                (Q(room__support_staff__isnull=True) & Q(room__is_active=True))
            ).order_by('timestamp')
        # Regular users can only see messages in their own rooms
        return ChatMessage.objects.filter(
            room__user=user
        ).order_by('timestamp')
    
    def perform_create(self, serializer):
        # Get the room ID from the request
        room_id = self.request.data.get('room_id')
        room = get_object_or_404(ChatRoom, room_id=room_id)
        
        # Check if user is authorized to send messages in this room
        if not (self.request.user == room.user or self.request.user == room.support_staff or
                (hasattr(self.request.user, 'support_profile') and room.support_staff is None)):
            return Response(
                {'error': 'Not authorized to send messages in this room'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the room's updated_at timestamp
        room.updated_at = timezone.now()
        room.save()
        
        # Create the message
        serializer.save(room=room, sender=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark messages as read
        """
        room_id = request.data.get('room_id')
        if not room_id:
            return Response(
                {'error': 'Room ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room = get_object_or_404(ChatRoom, room_id=room_id)
        # Mark all messages not sent by the current user as read
        ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({'status': 'messages marked as read'})

class SupportStaffViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for support staff (read-only)
    """
    queryset = SupportStaff.objects.filter(is_online=True, is_available=True)
    serializer_class = SupportStaffSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def set_status(self, request):
        """
        Set support staff status (online/offline, available/unavailable)
        """
        if not hasattr(request.user, 'support_profile'):
            return Response(
                {'error': 'Only support staff can update status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        staff = request.user.support_profile
        is_online = request.data.get('is_online')
        is_available = request.data.get('is_available')
        
        if is_online is not None:
            staff.is_online = is_online
        
        if is_available is not None:
            staff.is_available = is_available
        
        staff.save()
        return Response(SupportStaffSerializer(staff).data)
