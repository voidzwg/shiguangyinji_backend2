from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    nickname = models.CharField(default="", max_length=255)
    introduction = models.CharField(default="", max_length=255)
    article = models.IntegerField(default=0)
    fans = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/avatar.png', blank=True, null=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username
