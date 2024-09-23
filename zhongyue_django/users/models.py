from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1)
    remark = models.CharField(max_length=500, blank=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'status': self.status,
            'remark': self.remark
        }

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True)
    avatar = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    sex = models.IntegerField(choices=((0, '男'), (1, '女')), default=0)
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1)
    dept_id = models.IntegerField(null=True, blank=True)
    remark = models.CharField(max_length=500, blank=True)
    roles = models.JSONField(default=list)  # 修改为 JSONField

    def __str__(self):
        return self.user.username

    def to_dict(self):
        return {
            'id': self.user.id,
            'username': self.user.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'email': self.user.email,
            'phone': self.phone,
            'sex': self.sex,
            'status': self.status,
            'dept': {
                'id': self.dept_id,
                'name': 'Department Name'  # 这里需要根据实际情况获取部门名称
            },
            'remark': self.remark,
            'createTime': self.user.date_joined.timestamp() * 1000,
            'roles': self.roles  # 直接返回 roles 列表
        }

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
