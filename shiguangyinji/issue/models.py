from django.db import models
from django.contrib.auth.models import AbstractUser
from usermanage.models import User

class Issue(models.Model):
    issue_id = models.AutoField(db_column='id', primary_key=True)
    author = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    pictures = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Issue'