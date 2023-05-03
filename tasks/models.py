from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    creacion = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion=models.DateTimeField(null=True,blank=True)
    importante = models.BooleanField(default=False)
    #cascade por si se borra el usuario, se borran sus registros
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
      return self.titulo+" - del usuario "+self.usuario.username