from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # =====================================================
    # 🔥 NEW — STATE MACHINE FIELDS
    # =====================================================

    food_type = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    quantity = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    pickup_time = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    awaiting_confirmation = models.BooleanField(default=False)

    donation_created = models.BooleanField(default=False)

    # =====================================================

    def __str__(self):
        return f"Chat Session - {self.user.username} - {self.created_at}"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"