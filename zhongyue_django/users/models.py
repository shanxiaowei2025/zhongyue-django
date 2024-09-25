from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True)
    avatar = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    sex = models.IntegerField(choices=((0, '男'), (1, '女')), default=0)
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1)
    dept_id = models.IntegerField(null=True, blank=True)
    remark = models.CharField(max_length=500, blank=True)
    roles = models.JSONField(default=list)
    user_groups = models.JSONField(default=list)  # 将 groups 合并到 User 模型中
    user_permissions = models.JSONField(default=list)  # 将 permissions 合并到 User 模型中

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'email': self.email,
            'phone': self.phone,
            'sex': self.sex,
            'status': self.status,
            'dept': {
                'id': self.dept_id,
                'name': 'Department Name'  # 这里需要根据实际情况获取部门名称
            },
            'remark': self.remark,
            'createTime': self.date_joined.timestamp() * 1000,
            'roles': self.roles,
            'user_groups': self.user_groups,  # 添加 groups 字段
            'user_permissions': self.user_permissions  # 添加 permissions 字段
        }

    # 添加这两行来覆盖默认的多对多关系
    groups = None
    user_permissions = None
    


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

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1)
    remark = models.CharField(max_length=500, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
