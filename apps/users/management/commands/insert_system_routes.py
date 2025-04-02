from django.core.management.base import BaseCommand
from users.models import AsyncRoute

class Command(BaseCommand):
    help = 'Insert system management routes into the database'

    def handle(self, *args, **options):
        system_route = AsyncRoute.objects.create(
            path="/system",
            meta={
                "icon": "ri:settings-3-line",
                "title": "menus.pureSysManagement",
                "rank": "system"
            }
        )

        children = [
            {
                "path": "/system/user/index",
                "name": "SystemUser",
                "meta": {
                    "icon": "ri:admin-line",
                    "title": "menus.pureUser",
                    "roles": ["admin"]
                }
            },
            {
                "path": "/system/role/index",
                "name": "SystemRole",
                "meta": {
                    "icon": "ri:admin-fill",
                    "title": "menus.pureRole",
                    "roles": ["admin"]
                }
            },
            {
                "path": "/system/menu/index",
                "name": "SystemMenu",
                "meta": {
                    "icon": "ep:menu",
                    "title": "menus.pureSystemMenu",
                    "roles": ["admin"]
                }
            },
            {
                "path": "/system/dept/index",
                "name": "SystemDept",
                "meta": {
                    "icon": "ri:git-branch-line",
                    "title": "menus.pureDept",
                    "roles": ["admin"]
                }
            }
        ]

        for child in children:
            AsyncRoute.objects.create(
                path=child["path"],
                name=child["name"],
                meta=child["meta"],
                parent=system_route
            )

        self.stdout.write(self.style.SUCCESS('Successfully inserted system management routes'))