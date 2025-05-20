from django.contrib import admin
from .models import LineUser

@admin.register(LineUser)
class LineUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'line_user_id', 'is_active']
