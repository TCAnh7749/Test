from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    # A session can be linked to a logged-in user or just a session key for anonymous users
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"ChatSession {self.id} - {self.user.username if self.user else self.session_key}"

class Message(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, help_text="Null means it's from the customer")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg {self.id} by {'Admin' if self.is_admin else 'Customer'}"
