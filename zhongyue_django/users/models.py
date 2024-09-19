from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True)
    avatar = models.URLField(blank=True)
    roles = models.JSONField(default=list)
    permissions = models.JSONField(default=list)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class AsyncRoute(models.Model):
    path = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    component = models.CharField(max_length=255, null=True, blank=True)
    redirect = models.CharField(max_length=255, null=True, blank=True)
    meta = models.JSONField(default=dict)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.path

    def to_dict(self):
        result = {
            'path': self.path,
            'name': self.name,
            'component': self.component,
            'redirect': self.redirect,
            'meta': self.meta,
        }
        children = self.asyncroute_set.all()
        if children:
            result['children'] = [child.to_dict() for child in children]
        return result
