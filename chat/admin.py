from django.contrib import admin
from .models import ChatSession, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    inlines = [MessageInline]
    search_fields = ['session_key']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender', 'is_admin', 'timestamp']
    list_filter = ['is_admin', 'timestamp']
    search_fields = ['content']
