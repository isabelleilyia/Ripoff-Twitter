import json
import datetime
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from operator import attrgetter
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import User, Post, Follower, Like



def index(request):
    posts = Post.objects.all().order_by('-time')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    liked = []
    if request.user.is_authenticated:
        for post in posts:
            if(Like.objects.filter(user=request.user, post=post)):
                liked.append(post.id)
    print(liked)
    return render(request, "network/index.html", {
       "page_obj": page_obj,
       "user":request.user,
       "liked_posts": liked,
       "main": True

    })

@login_required
def create(request):
    #Get post information and update database
    text = request.POST["newPost"]
    p = Post(user=request.user, text=text, time=datetime.datetime.now())
    p.save()
    return HttpResponseRedirect(reverse("index"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(user=user).order_by('-time')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    owner = False
    if int(user.id) == int(request.user.id):
        owner = True
    is_following = False
    if Follower.objects.filter(following=user.id, follower=request.user):
        is_following = True
    followers = Follower.objects.filter(following=user.id)
    following = Follower.objects.filter(follower=user.id)
    liked = []
    for post in posts:
        if(Like.objects.filter(user=request.user, post=post)):
            liked.append(post.id)
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "posts_num": len(posts),
        "username":username,
        "is_owner": owner,
        "followers": len(followers),
        "following": len(following),
        "is_following": is_following,
        "profile": True,
        "liked_posts": liked
    })

@login_required
def follow(request, username):
    following = User.objects.get(username=username)
    if Follower.objects.filter(follower=request.user, following=following):
        Follower.objects.get(follower=request.user, following=following).delete()
    else:
        f = Follower(follower=request.user, following=following)
        f.save()
    return HttpResponseRedirect(reverse("profile", args=(username,)))

def following_posts(request):
    following = Follower.objects.filter(follower=request.user)
    posts=[]
    for person in following:
        post=Post.objects.filter(user=person.following)
        for item in post:
            posts.append(item)
    posts = sorted(posts, key=attrgetter("time"), reverse=True)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    liked = []
    for post in posts:
        if(Like.objects.filter(user=request.user, post=post)):
            liked.append(post.id)
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "following_page": True,
        "user":request.user,
        "liked_posts":liked
    })

@login_required
@csrf_exempt
def edit_post(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    if data.get("user") != request.user.username:
        return JsonResponse({"error": "You do not have permission to edit this post."}, status=400)
    
    updated = data.get("body")
    post = Post.objects.get(id=data.get("id"))
    post.text = updated
    post.save()
    return JsonResponse({"message": "Post updated successfully."}, status=201)

@csrf_exempt
@login_required
def update_like(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    post = Post.objects.get(id=data.get("post"))
    liked = data.get("liked")
    if liked==False:
        like = Like(user=request.user, post=post)
        like.save()
        post.likes +=1
        post.save()
        return JsonResponse({"message": "Like count updated successfully."}, status=400)
    else:
        Like.objects.filter(user=request.user,post=post).delete()
        post.likes -=1
        post.save()
        return JsonResponse({"message": "Like count updated successfully."}, status=400)
