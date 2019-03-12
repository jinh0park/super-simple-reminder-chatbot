from django.db import models


class ChatUser(models.Model):
    chat_id = models.CharField(max_length=15, unique=True)


class Todo(models.Model):
    chat_user = models.ForeignKey(
        'ChatUser',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    done = models.BooleanField(default=False)