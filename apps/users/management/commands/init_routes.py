from django.core.management.base import BaseCommand
from users.models import AsyncRoute

class Command(BaseCommand):
    help = 'Initialize async routes in the database'

    def handle(self, *args, **options):
        # 清除现有路由
        AsyncRoute.objects.all().delete()

        # 创建权限管理路由
        permission_route = AsyncRoute.objects.create(
            path="/permission",
            meta={
                "title": "权限管理",
                "icon": "ep:lollipop",
                "rank": 10
            }
        )

        # 创建子路由
        AsyncRoute.objects.create(
            path="/permission/page/index",
            name="PermissionPage",
            parent=permission_route,
            meta={
                "title": "页面权限",
                "roles": ["admin", "common"]
            }
        )

        button_route = AsyncRoute.objects.create(
            path="/permission/button",
            parent=permission_route,
            meta={
                "title": "按钮权限",
                "roles": ["admin", "common"]
            }
        )

        AsyncRoute.objects.create(
            path="/permission/button/router",
            component="permission/button/index",
            name="PermissionButtonRouter",
            parent=button_route,
            meta={
                "title": "路由返回按钮权限",
                "auths": [
                    "permission:btn:add",
                    "permission:btn:edit",
                    "permission:btn:delete"
                ]
            }
        )

        AsyncRoute.objects.create(
            path="/permission/button/login",
            component="permission/button/perms",
            name="PermissionButtonLogin",
            parent=button_route,
            meta={
                "title": "登录接口返回按钮权限"
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully initialized async routes'))
