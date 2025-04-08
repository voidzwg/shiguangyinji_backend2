from django.db import models
from django.contrib.auth.models import AbstractUser

class Issue(models.Model):
    issue_id = models.AutoField(db_column='id', primary_key=True)
    author = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    pictures = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Issue'


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