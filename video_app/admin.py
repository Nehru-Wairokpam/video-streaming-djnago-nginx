

# Register your models here.
from django.contrib import admin
from .models import Video
@admin.register(Video)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('title',)
