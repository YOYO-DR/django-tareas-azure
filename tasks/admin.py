from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    #para mostrar un atributo oculto del modelo en el admin, en este caso, created pero de solo lectura
    readonly_fields = ("creacion",)

admin.site.register(Task, TaskAdmin)
# Register your models here.
