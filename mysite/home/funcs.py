from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from . import models
from django.http import *
from django.contrib.auth.models import User
import datetime


def SendActivationLink(request):
    if request.user.is_authenticated == False:
        print("USER NOT AUTHENTICATED")
        return False

    username = request.user.username
    email = request.user.profile.email

    if email == "":
        print("EMAIL FALSE")
        return False

    emailQuery = models.EmailVerification.objects.filter(user=username)
    if len(emailQuery) != 1:
        print("EMAIL QUERY FALSE")
        return False

    activationCode = emailQuery[0].activation_code
    from_email = "no-reply@yeetboard.com"
    subject = "Welcome to YEETBOARD %s. Please activate your email address." % username
    to_email = email
    html_content = render_to_string('home/activation_template.html', {'username': username, 'activationCode': activationCode})
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    emailQuery[0].lastsent = datetime.datetime.now()
    emailQuery[0].save()


    return True

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print(ip)
    return ip
