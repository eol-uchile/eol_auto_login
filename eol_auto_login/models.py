from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class EolAutoLogin(models.Model):
    uuid = models.CharField(max_length=100, unique=True, blank=False, null=False)
    user = models.OneToOneField(
        User,
        db_index=True,
        on_delete=models.CASCADE,
        blank=False,
        null=False)
