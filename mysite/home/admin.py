from django.contrib import admin
from home.models import Profile, EmailVerification, Post, UserActions

admin.site.register(Profile)
admin.site.register(EmailVerification)
admin.site.register(Post)
admin.site.register(UserActions)
