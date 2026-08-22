from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from clinic.permissions import ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Create or refresh the eye-clinic role permission groups."

    def handle(self, *args, **options):
        for role, permission_policy in ROLE_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=role)
            if permission_policy == "all":
                permissions = Permission.objects.all()
            else:
                permission_ids = []
                for permission_label in permission_policy:
                    app_label, codename = permission_label.split(".", 1)
                    permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                    permission_ids.append(permission.pk)
                permissions = Permission.objects.filter(pk__in=permission_ids)
            group.permissions.set(permissions)
            self.stdout.write(f"{group.name}: {group.permissions.count()} permissions")
        self.stdout.write(self.style.SUCCESS(f"Configured {len(ROLE_PERMISSIONS)} clinic roles."))
