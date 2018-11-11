from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, User
)
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    email = models.TextField(max_length=50, blank=True)
    isActivated = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class EmailVerification(models.Model):
    user = models.CharField(max_length = 150, default="");
    activation_code = models.CharField(max_length = 50)
    redeemed = models.BooleanField(default = False)
    lastsent = models.DateTimeField(null=True)
class Post(models.Model):
    author = models.CharField(max_length = 32, blank=False)
    title = models.CharField(max_length = 200, blank=False)
    content = models.TextField(max_length = 5000, blank=True)
    timestamp = models.DateTimeField(null=False)
    isNsfw = models.BooleanField(default=False)
    isSpoiler = models.BooleanField(default=False)
    post_id = models.CharField(max_length=7, blank=False)
    def as_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp,
            "isNsfw": self.isNsfw,
            "isSpoiler": self.isSpoiler,
            "post_id": self.post_id
        }

class UserActions(models.Model):
    user = models.CharField(max_length = 32, blank=False, default="<GUEST>")
    action = models.CharField(max_length = 256, blank=False)
    timestamp = models.DateTimeField(null=False)
    ipv4 = models.CharField(max_length = 16, blank=False)
