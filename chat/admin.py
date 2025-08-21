from django.contrib import admin
from .models import ChatRoom, ChatMessage, SupportStaff

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'timestamp', 'is_read')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'name', 'user', 'support_staff', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('room_id', 'name', 'user__username', 'support_staff__username')
    readonly_fields = ('room_id', 'user', 'created_at', 'updated_at')
    inlines = [ChatMessageInline]
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room_id', 'name', 'user', 'support_staff', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'room', 'sender', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'room')
    search_fields = ('message', 'sender__username')
    readonly_fields = ('room', 'sender', 'timestamp')

@admin.register(SupportStaff)
class SupportStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'is_available', 'max_concurrent_chats', 'last_activity', 'current_chat_count')
    list_filter = ('is_online', 'is_available')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_activity', 'current_chat_count')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Status', {
            'fields': ('is_online', 'is_available', 'max_concurrent_chats')
        }),
        ('Activity', {
            'fields': ('last_activity', 'current_chat_count'),
            'classes': ('collapse',)
        }),
    )
    
    def current_chat_count(self, obj):
        return obj.current_chat_count
    current_chat_count.short_description = 'Active Chats'
