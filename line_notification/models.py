from django.db import models
from django.contrib.auth.models import User

class LineUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    line_user_id = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
