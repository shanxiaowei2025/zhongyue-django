from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

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
    is_expense_auditor = models.BooleanField(default=False, verbose_name="是否为费用审核员")
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
            'user_permissions': self.user_permissions,  # 添加 permissions 字段
            'is_expense_auditor': self.is_expense_auditor
        }

    # 添加这两行来覆盖默认的多对多关系
    groups = None
    user_permissions = None

    def has_role(self, role_name):
        return role_name in self.roles
    class Meta:
        db_table = 'zy_user'

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
    class Meta:
        db_table = 'zy_async_route'

class Role(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='角色ID', db_comment='角色ID')
    name = models.CharField(max_length=50, unique=True, default='', verbose_name='角色名称', db_comment='角色名称')
    code = models.CharField(max_length=50, unique=True, default='', verbose_name='角色代码', db_comment='角色唯一代码')
    status = models.IntegerField(choices=((0, '禁用'), (1, '启用')), default=1, verbose_name='状态', db_comment='角色状态：0-禁用，1-启用')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注', db_comment='角色备注信息')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_comment='角色创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_comment='角色最后更新时间')

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'zy_role'

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
        db_table = 'zy_department'

class Permission(models.Model):
    """权限表"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions', verbose_name='角色', db_comment='关联的角色')
    role_name = models.CharField(max_length=50, verbose_name='角色名称', db_comment='角色名称')
    page_name = models.CharField(max_length=50, verbose_name='页面名称', db_comment='权限所属的页面名称，如：合同管理')
    permission_name = models.CharField(max_length=100, verbose_name='权限名称', db_comment='权限名称，如：contract_data_view_all')
    permission_value = models.BooleanField(default=False, verbose_name='权限值', db_comment='是否拥有该权限')
    description = models.CharField(max_length=200, verbose_name='权限描述', db_comment='权限的中文描述')

    class Meta:
        db_table = 'zy_permission'
        unique_together = ('role', 'permission_name')
        ordering = ['page_name', 'permission_name']

    def __str__(self):
        return f"{self.role_name} - {self.page_name} - {self.description}"

    def to_dict(self):
        """返回单个权限记录的字典表示"""
        return {
            'role_name': self.role_name,
            'page_name': self.page_name,
            'permission_name': self.permission_name,
            'permission_value': self.permission_value,
            'description': self.description
        }

    def save(self, *args, **kwargs):
        if not self.role_name:
            self.role_name = self.role.name
        super().save(*args, **kwargs)

@receiver(post_save, sender=Role)
def create_or_update_permission(sender, instance, created, **kwargs):
    """当角色创建或更新时，同步更新权限"""
    if created:
        # 获取现有的所有权限名称和描述
        existing_permissions = Permission.objects.exclude(role=instance).values(
            'permission_name', 'description', 'page_name'
        ).distinct()
        
        # 为新角色创建所有权限记录
        for perm in existing_permissions:
            Permission.objects.create(
                role=instance,
                role_name=instance.name,
                page_name=perm['page_name'],
                permission_name=perm['permission_name'],
                description=perm['description'],
                permission_value=False  # 默认无权限
            )
    else:
        # 更新角色时，只更新角色名称
        Permission.objects.filter(role=instance).update(role_name=instance.name)

@receiver(post_delete, sender=Role)
def delete_role_permissions(sender, instance, **kwargs):
    """当角色被删除时，同步删除权限记录"""
    try:
        Permission.objects.filter(role_name=instance.name).delete()
    except Exception as e:
        print(f"Error in delete_role_permissions: {str(e)}")

# 确保信号被注册
Role.post_save = post_save.connect(create_or_update_permission, sender=Role)
Role.post_delete = post_delete.connect(delete_role_permissions, sender=Role)
