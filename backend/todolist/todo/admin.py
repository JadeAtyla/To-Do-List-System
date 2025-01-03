from django.contrib import admin
from todo.models import Todo

# Register your models here.
class TodoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'completed', 'deleted', 'created_at', 'updated_at')

admin.site.register(Todo, TodoAdmin)