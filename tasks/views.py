from django.shortcuts import render, redirect,get_object_or_404
#lib para crear formulario para la creacion de un usuario
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
#el login no crea un usuario, esto crea las cookies para el inicio de sesión
from django.contrib.auth import login,logout,authenticate
from django.db import IntegrityError
from tasks.forms import TaskForm
from tasks.models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required #con este decorador no lo dejo entrar a mis vistas si no esta logueado, lo pongo arriba de mi vista para decirle que para entrar a esa vista debe estar logueado y lo va a redireccionar al login que debe estar acomodado en settings.py

def home(request):
  return render(request,'home.html')

def signup(request):
  if request.method == 'GET':
    #si el metodo es get, le paso el formulario
    return render(request,'signup.html',{
    'form': UserCreationForm
  })
  else:
    #comparo las contraseñas recibidas
    if request.POST['password1']==request.POST['password2']:
      # registrando usuario
      #esto crea un usuario, y tambien cifra la contraseña pero todavia no lo guarda en la base de datos
      try:
        user=User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
      #asi ya lo guarda
        user.save()
        #despues de guardar el usuario, al login (para que guarde las credenciales o cookies en el navegador, le paso a la funcion login, el request y el usuario/objeto que cree)
        login(request,user)
        #lo redirecciono a la url con ese 'name'
        return redirect('tasks')
      
      except IntegrityError:
        #asi más manejo errores más especificos, los de Integrity son errores con la base de datos
        return render(request,'signup.html',{
    'form': UserCreationForm,
    'error':'El usuario ya existe'
  })
    else:
      return render(request,'signup.html',{
    'form': UserCreationForm,
    'error':'La contraseña no coinciden'
  })

@login_required
def tasks(request):
  #asi me trae las tareas que sean solo del usuario actual
  task=Task.objects.filter(usuario=request.user,fecha_finalizacion__isnull=True)
  return render(request,'tasks.html',{'tasks':task,'title':'Tareas pendientes'})

@login_required
def tasks_completed(request):
  #asi me trae las tareas que sean solo del usuario actual
  task=Task.objects.filter(usuario=request.user,fecha_finalizacion__isnull=False).order_by('-fecha_finalizacion')
  return render(request,'tasks.html',{'tasks':task,'title':'Tareas completadas'})

@login_required
def create_task(request):
  if request.method=='GET':
    return render(request,'create_task.html',{
    'form':TaskForm
  })
  else:
    try:
      #esto crea un formulario
      form = TaskForm(request.POST)
    #con el sabe lo guardo en la base de datos, pero con el commit en falso, no se guarda en la base de datos, sino que en la variable que le asigne nomás para prueba
    # new_task = form.save(commit=False)
    #porque el modelo necesita el usuario, y cuando el usuario esta logueado, la clase del usuario siempre esta en el request como "request.user"
      new_task = form.save(commit=False)
      new_task.usuario=request.user
      new_task.save()
      return redirect('tasks')
    except ValueError:
      return render(request,'create_task.html',{
    'form':TaskForm,
    'error':'Por favor provee un dato valido'
  })

#recibe ese id o parametro de la url (task_id)

@login_required
def task_detail(request,task_id):
  if request.method=="GET":
  #esta funcion, le paso el modelo y el filtro o como lo llamo con el orm de object.get, y si no lo encuentra, simplemente le dice un 404, y si lo encuntra, muestra los valores, y asi no tumba el servidor por si no encuentra esa tarea con su llave primaria
  #al comparar el user con el request.user, que es el usuario logueado, puedo decirle que la tarea a buscar debe tener un id y ademas que el user al cual pertenece esa tarea tambien debe conincidir con el user el cual esta logueado y asi no accede a tareas de otros usuarios
    task = get_object_or_404(Task,pk=task_id, usuario=request.user)
  #crear formulario apartir de los datoss recibidos del usuario anteriormente para editarlo
    form = TaskForm(instance=task)
    return render(request,'task_detail.html',{'task':task,'form':form})
  else:
    try:
    #obtengo el objeto/registro de la tarea
      task = get_object_or_404(Task, pk=task_id, usuario=request.user)
      #creo una instacia del formulario como cuando creamos el formulario, nomas que le paso los datos actualizados y que la instancia o tarea es la que conseguimos
      form=TaskForm(request.POST,instance=task)
      form.save()
      return redirect('tasks')
    except ValueError:
      return render(request,'task_detail.html',{'task':task,'form':form,'error':'Error actualizando la tarea'})

@login_required
def complete_task(request,task_id):
#obtengo la tarea
  task=get_object_or_404(Task,pk=task_id,usuario=request.user)
  #si visita la pagina (o lo mando a ella)
  if request.method=='POST':
    #con el timezone.now() le pongo la fecha de hoy, es una lib de django, y luego guardo ese valor actualizado
    task.fecha_finalizacion=timezone.now()
    task.save()
    return redirect('tasks_completed')

@login_required
def delete_task(request,task_id):
#obtengo la tarea
  task=get_object_or_404(Task,pk=task_id,usuario=request.user)
  #si visita la pagina (o lo mando a ella)
  if request.method=='POST':
    #si encontro la tarea, borrala
    task.delete()
    return redirect('tasks')

@login_required
def signout(request):
  logout(request) #con esto cerro la sesión
  return redirect('home')

def signin(request):
  if request.method=='GET':
    return render(request,'signin.html',{
    #Para iniciar sesion
    'form': AuthenticationForm
  })
  else:
    user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
    #si no encontro nada (usuario no existe o contraseña incorrecta)
    if user == None:
      return render(request,'signin.html',{
    #Para iniciar sesion
    'form': AuthenticationForm,
    'error':'Usuario o contraseña incorrectos'
  })
    else:
      #antes de mandarlo a tasks porque el usuario si existe, creo la sesión
      login(request,user)
      return redirect('tasks')