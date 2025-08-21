from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    """
    Represents a chat room for conversations between users and support staff.
    """
    name = models.CharField(max_length=100)
    # A unique identifier for the room
    room_id = models.CharField(max_length=100, unique=True)
    # The user who initiated the chat
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    # The support staff assigned to this room, can be null if not assigned yet
    support_staff = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='support_rooms'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat {self.room_id} - {self.user.username}"
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['room_id']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['support_staff', 'is_active']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at'])
        ]

class ChatMessage(models.Model):
    """
    Represents a message in a chat room.
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
            models.Index(fields=['sender']),
            models.Index(fields=['room', 'is_read']),
            models.Index(fields=['timestamp'])
        ]

class SupportStaff(models.Model):
    """
    Represents a support staff member's additional information and status.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='support_profile')
    is_online = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    max_concurrent_chats = models.IntegerField(default=3)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Support: {self.user.username}"
    
    @property
    def current_chat_count(self):
        return self.support_rooms.filter(is_active=True).count()
    
    @property
    def can_take_new_chat(self):
        return self.is_online and self.is_available and self.current_chat_count < self.max_concurrent_chats

    class Meta:
        verbose_name_plural = 'Support Staff'
        indexes = [
            models.Index(fields=['is_online', 'is_available']),
            models.Index(fields=['user'])
        ]
