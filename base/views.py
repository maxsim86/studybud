from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.

# rooms = [
#    {'id':1, 'name':'lets learn python!'},
#    {'id':2, 'name':'Design wtih me!'},
#    {'id':3, 'name':'Frontend developer'},
# ]


# user login
def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "user does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "username OR password does not exits")
    context = {"page": page}
    return render(request, "base/login_register.html", context)


# user logout
def logoutUser(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error accurred during registrations')
            
    return render(request, "base/login_register.html", {'form':form})


def home(request):
    # filter by topic name, topic name take from models Room --.topic and then take a name of a topic
    # search by 3 deference value 1. search by topic 2. search by name and search by descriptions.

    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    # add topics at left sidebar
    topics = Topic.objects.all()

    # calculate total room available
    room_count = rooms.count()

    context = {"rooms": rooms, "topics": topics, "room_count": room_count}

    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    
    if request.method == "POST":
        # detail user, room dan body diambil dari Message models.py
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        return redirect('room', pk=room.id)
    
    context = {"room": room, "room_messages": room_messages }
    return render(request, "base/room.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()

    if request.method == "POST":
        # add data to the forms
        form = RoomForm(request.POST)
        # if form valid
        if form.is_valid():
            # then save a post data
            form.save()
            # redirect to home page
            return redirect("home")

    context = {"form": form}
    return render(request, "base/room_form.html", context)


def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    # only user yang betul boleh edit content
    if request.user != room.host:
        return HttpResponse("You are not allowed here !!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "base/room_form.html", context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})
