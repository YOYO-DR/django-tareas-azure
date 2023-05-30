from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# lib para crear formulario para la creacion de un usuario
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# el login no crea un usuario, esto crea las cookies para el inicio de sesión
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from tasks.forms import TaskForm
from tasks.models import Task
from django.utils import timezone
# con este decorador no lo dejo entrar a mis vistas si no esta logueado, lo pongo arriba de mi vista para decirle que para entrar a esa vista debe estar logueado y lo va a redireccionar al login que debe estar acomodado en settings.py
from django.contrib.auth.decorators import login_required

# vistas basadas en clases
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView, CreateView, UpdateView, View
from django.contrib.auth.views import LoginView, LogoutView
import json

# vista para las peticiónes de las tareas


class TaskViewView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        url = data.get('url')
        if url:
            url = url.split('/')
            url = '/' + '/'.join(url[3:])
        else:
            url = '/'
        mensaje = {}
        action = data.get('action')
        pk = data.get('pk')
        tarea = Task.objects.get(pk=pk)
        if not tarea:
            mensaje['errors'] = 'Tarea no encontrada'
        elif action == 'task_complete':
            tarea.fecha_finalizacion = timezone.now()
            tarea.save()
            mensaje['success_url'] = reverse_lazy('tasks_completed')
            mensaje['mensaje'] = 'tarea completada'
        elif action == 'borrar':
            tarea.delete()
            mensaje['success_url'] = url
            mensaje['mensaje'] = 'tarea eliminada'
        return JsonResponse(mensaje)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Bienvenido'
        return context


class SignupView(FormView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Registro'
        return context


class TastkListView(ListView):
    model = Task
    template_name = 'tasks.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        tasks = Task.objects.filter(
            usuario=user, fecha_finalizacion__isnull=True)
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'pendientes'
        return context


class TasksComplete(ListView):
    model = Task
    template_name = 'tasks.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        query = Task.objects.filter(
            usuario=user, fecha_finalizacion__isnull=False).order_by('-fecha_finalizacion')
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'completas'
        return context


class CreateTaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'create_task.html'
    success_url = reverse_lazy('tasks')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Crear tarea'
        return context

    def form_valid(self, form):
        # como tengo que ponerle el usuario al registro, obtengo la instacia del registro al gurdar, poninedole el commit en false, y en el atributo usuario le paso el usuario con el request y ahi si lo guardo y retorno a la vista del view
        task = form.save(commit=False)
        task.usuario = self.request.user
        task.save()
        return redirect(self.success_url)


class TaskDetailUpdateView(UpdateView):
    # el id que recibe por la url debe llamarse pk, y eso va en el kwargs
    model = Task
    form_class = TaskForm
    template_name = 'task_detail.html'
    success_url = reverse_lazy('tasks')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url').split('/')
        url = '/' + '/'.join(url[3:])
        self.success_url = url
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # la tarea u objeto se obtiene de la funcion get_context_data y se guarda como object
        tituloTarea = context["object"].titulo
        context["title"] = f'Tarea {tituloTarea}'
        return context


class SigninView(LoginView):
    template_name = 'signin.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # si esta logueado lo mando a la vista principal
            return redirect('store')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Iniciar sesión'
        return context


# def signin(request):
#     if request.method == 'GET':
#         return render(request, 'signin.html', {
#             # Para iniciar sesion
#             'form': AuthenticationForm
#         })
#     else:
#         user = authenticate(
#             request, username=request.POST['username'], password=request.POST['password'])
#         # si no encontro nada (usuario no existe o contraseña incorrecta)
#         if user == None:
#             return render(request, 'signin.html', {
#                 # Para iniciar sesion
#                 'form': AuthenticationForm,
#                 'error': 'Usuario o contraseña incorrectos'
#             })
#         else:
#             # antes de mandarlo a tasks porque el usuario si existe, creo la sesión
#             login(request, user)
#             return redirect('tasks')
