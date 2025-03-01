from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.utils.datetime import get_expiry_time

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, primary_key=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiry_time)

    def __str__(self):
        return self.email