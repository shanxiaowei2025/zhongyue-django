from django.contrib.auth.models import Group

def get_user_permissions(user, current_role=None):
    """
    根据用户角色获取客户信息管理的权限配置。

    参数:
    user (User): 当前用户对象
    current_role (str): 当前角色名称（可选）

    返回:
    dict: 包含用户权限的字典
    """
    # 初始化权限字典，默认所有权限为 False
    permissions = {
        'actions': {
            'edit': False,      # 编辑权限
            'delete': False,    # 删除权限
            'viewDetails': False  # 查看详细信息权限
        },
        'data': {
            'viewAll': False,   # 查看所有数据权限
            'viewOwn': False,   # 查看自己创建的数据权限
            'viewByLocation': None,  # 按地点查看数据权限
            'viewDepartmentSubmissions': False  # 查看部门创建的数据权限
        }
    }

    # 根据用户角色设置相应的权限
    if user.is_superuser or user.has_role('管理员'):
        # 超级用户或管理员拥有所有权限
        permissions['actions'] = {k: True for k in permissions['actions']}
        permissions['data']['viewAll'] = True
    elif user.has_role('客户经理'):
        # 客户经理的权限设置
        permissions['actions']['edit'] = True
        permissions['actions']['viewDetails'] = True
        permissions['data']['viewOwn'] = True
    elif user.has_role('雄安分公司负责人'):
        # 雄安分公司负责人的权限设置
        permissions['actions']['edit'] = True
        permissions['actions']['delete'] = True
        permissions['actions']['viewDetails'] = True
        permissions['data']['viewByLocation'] = '雄安'
        permissions['data']['viewDepartmentSubmissions'] = True
    elif user.has_role('高碑店分公司负责人'):
        # 高碑店分公司负责人的权限设置
        permissions['actions']['edit'] = True
        permissions['actions']['delete'] = True
        permissions['actions']['viewDetails'] = True
        permissions['data']['viewByLocation'] = '高碑店'
        permissions['data']['viewDepartmentSubmissions'] = True

    return permissions
