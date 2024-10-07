from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, default='', verbose_name='昵称', db_comment='用户昵称')
    avatar = models.URLField(blank=True, default='', verbose_name='头像URL', db_comment='用户头像URL')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='电话号码', db_comment='用户电话号码')
    sex = models.IntegerField(choices=((0, '男'), (1, '女')), default=0, verbose_name='性别', db_comment='用户性别：0-男，1-女')
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1, verbose_name='状态', db_comment='用户状态：0-禁用，1-启用')
    dept_id = models.IntegerField(null=True, blank=True, default=None, verbose_name='部门ID', db_comment='用户所属部门ID')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注', db_comment='用户备注信息')
    roles = models.JSONField(default=list, verbose_name='角色列表', db_comment='用户角色列表，JSON格式')
    user_groups = models.JSONField(default=list, verbose_name='用户组列表', db_comment='用户组列表，JSON格式')
    user_permissions = models.JSONField(default=list, verbose_name='用户权限列表', db_comment='用户权限列表，JSON格式')

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

    def has_role(self, role_name):
        return role_name in self.roles

class AsyncRoute(models.Model):
    path = models.CharField(max_length=255, default='', verbose_name='路由路径', db_comment='异步路由路径')
    name = models.CharField(max_length=255, null=True, blank=True, default=None, verbose_name='路由名称', db_comment='异步路由名称')
    component = models.CharField(max_length=255, null=True, blank=True, default=None, verbose_name='组件路径', db_comment='异步路由对应的组件路径')
    redirect = models.CharField(max_length=255, null=True, blank=True, default=None, verbose_name='重定向路径', db_comment='异步路由重定向路径')
    meta = models.JSONField(default=dict, verbose_name='路由元数据', db_comment='异步路由元数据，JSON格式')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, default=None, verbose_name='父路由', db_comment='父级异步路由ID')

    def __str__(self):
        return self.path

    def to_dict(self):
        result = {
            'path': self.path,
            'name': self.name,
            'component': self.component if self.component else None,
            'redirect': self.redirect if self.redirect else None,
            'meta': self.meta,
        }
        children = self.asyncroute_set.all()
        if children:
            result['children'] = [child.to_dict() for child in children]
        return result

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, default='', verbose_name='角色名称', db_comment='角色名称')
    code = models.CharField(max_length=50, unique=True, default='', verbose_name='角色代码', db_comment='角色唯一代码')
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1, verbose_name='状态', db_comment='角色状态：0-禁用，1-启用')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注', db_comment='角色备注信息')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_comment='角色创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_comment='角色最后更新时间')

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100, default='', verbose_name='部门名称', db_comment='部门名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', default=None, verbose_name='父部门', db_comment='父级部门ID')
    sort = models.IntegerField(default=0, verbose_name='排序', db_comment='部门排序值')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='联系电话', db_comment='部门联系电话')
    principal = models.CharField(max_length=100, blank=True, default='', verbose_name='负责人', db_comment='部门负责人')
    email = models.EmailField(blank=True, default='', verbose_name='邮箱', db_comment='部门联系邮箱')
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1, verbose_name='状态', db_comment='部门状态：0-禁用，1-启用')
    type = models.IntegerField(choices=((1, '公司'), (2, '分公司'), (3, '部门')), default=3, verbose_name='类型', db_comment='部门类型：1-公司，2-分公司，3-部门')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_comment='部门创建时间')
    remark = models.TextField(blank=True, default='', verbose_name='备注', db_comment='部门备注信息')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort', 'id']
