from rest_framework import serializers
from .models import ChatRoom, ChatMessage, SupportStaff
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information in chat context
    """
    is_support = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'is_support']
    
    def get_is_support(self, obj):
        return hasattr(obj, 'support_profile')

class SupportStaffSerializer(serializers.ModelSerializer):
    """
    Serializer for support staff information
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SupportStaff
        fields = ['user', 'is_online', 'is_available', 'current_chat_count', 'can_take_new_chat']

class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages
    """
    sender = UserSerializer(read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'message', 'timestamp', 'formatted_timestamp', 'is_read']
        read_only_fields = ['id', 'room', 'sender', 'timestamp', 'formatted_timestamp']
    
    def get_formatted_timestamp(self, obj):
        return obj.timestamp.strftime("%b %d, %Y %H:%M")

class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for chat rooms
    """
    user = UserSerializer(read_only=True)
    support_staff = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'room_id', 'name', 'user', 'support_staff', 'is_active', 
                 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['id', 'room_id', 'user', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        try:
            message = obj.messages.order_by('-timestamp').first()
            if message:
                return ChatMessageSerializer(message).data
            return None
        except ChatMessage.DoesNotExist:
            return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class ChatRoomWithMessagesSerializer(ChatRoomSerializer):
    """
    Serializer for chat rooms with all messages
    """
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta(ChatRoomSerializer.Meta):
        fields = ChatRoomSerializer.Meta.fields + ['messages'] 