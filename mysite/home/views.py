from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import *
from django.contrib.auth.models import User
from . import models
import requests
import json
import random
import string
from home.funcs import SendActivationLink, get_client_ip
import datetime
from home.forms import PostForm
from mysite.settings import ReCaptcha_Secret

#SECURITY WARNING: SET TO TRUE DURING PRODUCITON
REQUIRE_VERIFIED_RECAPTCHA = True



# Create your views here.
def index(request):

    return render(request, 'home/index.html');
def getPosts(request):
    ammount = 25
    if(request.method == "GET"):
        if('startID' in request.GET):
            startID = request.GET['startID']
            try:
                startID = int(startID)
            except Exception:
                return HttpResponse("Invalid Start ID")
        else:
            startID = models.Post.objects.order_by('-id')[0].id

        PostList = list( models.Post.objects.filter(id__lte = startID).order_by('-id')[:ammount])
        ListData = [ obj.as_dict() for obj in PostList ]
        return HttpResponse(json.dumps(ListData, indent=4, sort_keys=True, default=str))
    else:
        return HttpResponse("Error: Get Request Only")

def register(request):
    args = {}
    args['recaptcha_errors'] = ""
    if request.method == 'POST':


        recaptcha_response = request.POST['g-recaptcha-response']
        site_verify = "https://www.google.com/recaptcha/api/siteverify"
        secret = ReCaptcha_Secret
        verify_data = {'secret': secret, 'response': recaptcha_response}
        response = requests.post(site_verify, verify_data)
        list_response = json.loads(response.content)

        form = UserCreationForm(request.POST)
        #print(list_response['success'])
        if(str(list_response['success']) != "True" and REQUIRE_VERIFIED_RECAPTCHA):
            args['recaptcha_errors'] = "Please Complete ReCaptcha Correctly"

        elif form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            uEmailActivate = models.EmailVerification()
            uEmailActivate.user = username

            tempCode = ""
            foundCode = False
            chars=string.ascii_uppercase + string.digits
            while foundCode == False:
                tempCode = ''.join(random.choice(chars) for _ in range(50))
                query = models.EmailVerification.objects.filter(activation_code=tempCode)
                if len(query) == 0:
                    foundCode = True
            uEmailActivate.activation_code = tempCode
            uEmailActivate.save()

            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    args['form'] = form
    #return HttpResponse("HEY BOI")
    return render(request, 'home/register.html', args)

def profile(request, user_name=""):
    args = {}
    args['isUser'] = True
    if(user_name != "" and user_name != ""):
        query = User.objects.filter(username=user_name)
        if(len(query) == 1):
            args["uname"] = query[0].username
            args["bio"] = query[0].profile.bio;
        else:
            args["uname"] = "User Not Found :("
            args["isUser"] = False

    elif(request.user.is_authenticated):
        args["uname"] = request.user.username
        args["bio"] = request.user.profile.bio
    else:
        return redirect("/")

    return render(request, 'home/profile.html', args)
def changeemail(request):
    args = {"email_errors": ""}
    if(request.method == "GET"):
        if(request.user.is_authenticated):
            return render(request, 'home/change_email.html', args)
        else:
            return redirect("/")
    elif(request.method == "POST" and request.user.is_authenticated):
        if(request.POST['email']):
            request.user.profile.email = request.POST['email']
            request.user.save()

            return redirect("/verify_email/send")
        return HttpResponse("POST")
    else:
        return redirect("/")

def send_verification(request):
    if(SendActivationLink(request)):
        return render(request, "home/message.html", {'type': 'Success', 'message': "Activation Code Sent"})
    else:
        return render(request, "home/message.html", {'type': 'ERROR', 'message': "Failed to send activation code"})
def activate_email(request, activation_code=""):

    if len(activation_code) != 50:
        return render(request, "home/message.html", {'type': 'ERROR', 'message': "Invalid Activation Code"})
    query = models.EmailVerification.objects.filter(activation_code=activation_code)
    if len(query) != 1:
        return render(request, "home/message.html", {'type': 'ERROR', 'message': "Invalid Activation Code"})
    if(query[0].redeemed):
        return render(request, "home/message.html", {'type': 'ERROR', 'message': "Invalid Activation Code"})
    username = query[0].user
    userObject = User.objects.filter(username=username)
    userObject = userObject[0]
    userObject.profile.isActivated = True
    userObject.save()
    query[0].redeemed = True
    query[0].save()

    return render(request, "home/message.html", {'type': 'Success', 'message': "Email has been verified"})

def submit_post(request):
    if(request.user.is_authenticated == False):
        return redirect("/signin")
    args = {'form_errors': [], 'recaptcha_errors': ''}
    if(request.method == "GET"):
        return render(request, "home/submit_post.html", args)
    elif(request.method == "POST"):

        is_nsfw = request.POST.get('isNsfw', False)
        is_spoiler = request.POST.get('isSpoiler', False)

        if(is_nsfw != False):
            is_nsfw = True
        if(is_spoiler != False):
            is_spoiler = True

        print("isNsfw: %s; isSpoiler: %s" % (is_nsfw, is_spoiler))

        form = PostForm(request.POST)
        valid = True

        recaptcha_response = request.POST['g-recaptcha-response']
        site_verify = "https://www.google.com/recaptcha/api/siteverify"
        secret = ReCaptcha_Secret
        verify_data = {'secret': secret, 'response': recaptcha_response}
        response = requests.post(site_verify, verify_data)
        list_response = json.loads(response.content)

        if(len(request.POST['title']) > 200 or len(request.POST['title']) == 0):
            valid=False
            args['form_errors'].append("Title must be 1-200 characters long")

        if(len(request.POST['content']) > 5000):
            valid=False
            args['form_errors'].append("Content must be 5000 characters or less")

        if(str(list_response['success']) != 'True' and REQUIRE_VERIFIED_RECAPTCHA):
            valid=False
            args['recaptcha_errors'] = "Please Complete ReCaptcha Correctly"

        if(valid and form.is_valid()):
            submited_post = models.Post()
            submited_post.author = request.user.username
            submited_post.title = request.POST['title']
            submited_post.content = request.POST['content']
            submited_post.timestamp = datetime.datetime.utcnow()
            submited_post.isNsfw = is_nsfw
            submited_post.isSpoiler = is_spoiler

            tempId = ""
            foundId = False
            chars=string.ascii_uppercase + string.ascii_lowercase + string.digits + '-' + '_'
            while foundId == False:
                tempId = ''.join(random.choice(chars) for _ in range(7))
                query = models.Post.objects.filter(post_id=tempId)
                if len(query) == 0:
                    foundId = True
            submited_post.post_id = tempId
            submited_post.save()

            return redirect("/")

        return render(request, "home/submit_post.html", args)

def fetchpost(request, postid=""):



    validPostId = True
    args = {'validPost': False}
    if(len(postid) != 7):
        validPostId = False
    query = models.Post.objects.filter(post_id = postid)
    if(len(query) != 1):
        validPostId = False
        args['postObject'] = False
    else:
        args['postObject'] = query[0]
    args['validPost'] = validPostId

    if(not validPostId):
        return render(request, "home/message.html", {'type': 'ERROR', 'message': 'Invalid Post ID'})

    return render(request, "home/view_post.html", args)

### SERVER ERROR HANDLING ###

#400 Error
def bad_request(request):
    args = {'type': '400', 'message': 'Bad Request'}
    return render(request, 'home/message.html', args)
#403 Error
def permission_denied(request):
    args = {'type': '403', 'message': 'Permission Denied'}
    return render(request, 'home/message.html', args)
#500 Error
def server_error(request):
    args = {'type': '500', 'message': 'Server Error'}
    return render(request, 'home/message.html', args)
#404 Error
def page_not_found(request):
    args = {'type': '404', 'message': 'Page Not Found', 'additional_message': ('Could not find page from path "%s"' % request.get_full_path())}
    return render(request, 'home/message.html', args)

### SERVER ERROR HANDLING END ###
