from django.contrib import admin
from .models import LineUser

@admin.register(LineUser)
class LineUserAdmin(admin.ModelAdmin):
    list_display = ['line_user_id', 'name']
    search_fields = ['line_user_id', 'name']
