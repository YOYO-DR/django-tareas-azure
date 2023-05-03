from django.urls import path
from tasks.views import *

urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('signup/',SignupView.as_view(),name='signup'),
    #cuando visite esa ruta, se va a cerrar sesión
    path('logout/',LogoutView.as_view(),name='logout'),
    path('signin/',signin,name='signin'),
    path('tasks/',TastkListView.as_view(),name='tasks'),
    path('tasks_completed/',tasks_completed,name='tasks_completed'),
    path('tasks/create/',create_task,name='create_tasks'),
    #con eso le digo que la ulr va a ser dinamica,en este caso le pondre el id de la tarea, y le pongo asi para que django sepa y le pongo un nombre
    path('tasks/<int:task_id>/',task_detail,name='task_detail'),
    path('tasks/<int:task_id>/complete',complete_task,name='complete_task'),
    path('tasks/<int:task_id>/delete',delete_task,name='delete_task'),
]
