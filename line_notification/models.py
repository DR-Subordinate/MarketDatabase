from django.db import models

class LineUser(models.Model):
    line_user_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name or self.line_user_id
