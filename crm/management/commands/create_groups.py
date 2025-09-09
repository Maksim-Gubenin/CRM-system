from typing import Any, Dict, List, Optional

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create initial groups and assign permissions"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(
            self.style.SUCCESS("Starting to create groups and permissions...")
        )

        custom_permission_created = self._create_custom_permission()
        if not custom_permission_created:
            self.stderr.write(
                self.style.ERROR("Failed to create custom permission. Aborting.")
            )
            return

        groups_config: Dict[str, List[str]] = {
            "Operator": [
                "leads.add_lead",
                "leads.change_lead",
                "leads.view_lead",
                "advertisements.view_advertisement_stats",
            ],
            "Marketer": [
                "products.add_product",
                "products.change_product",
                "products.view_product",
                "advertisements.add_advertisement",
                "advertisements.change_advertisement",
                "advertisements.view_advertisement",
                "advertisements.view_advertisement_stats",
            ],
            "Manager": [
                "leads.view_lead",
                "customers.view_customer",
                "customers.add_customer",
                "contracts.add_contract",
                "contracts.change_contract",
                "contracts.view_contract",
                "advertisements.view_advertisement_stats",
            ],
        }

        success = self._create_groups_with_permissions(groups_config)

        if success:
            self.stdout.write(
                self.style.SUCCESS("✓ All groups and permissions created successfully!")
            )
        else:
            self.stderr.write(
                self.style.ERROR(
                    "✗ Some groups or permissions were not created properly"
                )
            )

    def _create_custom_permission(self) -> bool:
        """Create custom permission for advertisement statistics"""
        try:
            ad_content_type, created = ContentType.objects.get_or_create(
                app_label="advertisements",
                model="advertisement",
                defaults={"name": "Advertisement"},
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS("✓ Created ContentType for advertisements")
                )

            perm, created = Permission.objects.get_or_create(
                codename="view_advertisement_stats",
                content_type=ad_content_type,
                defaults={"name": "Can view advertisement statistics"},
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created custom permission: {perm.codename}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"ℹ Custom permission already exists: {perm.codename}"
                    )
                )

            return True

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"✗ Error creating custom permission: {str(e)}")
            )
            return False

    def _create_groups_with_permissions(
        self, groups_config: Dict[str, List[str]]
    ) -> bool:
        """Create groups and assign permissions"""
        success = True

        for group_name, permission_codenames in groups_config.items():
            group_success = self._create_single_group(group_name, permission_codenames)
            if not group_success:
                success = False

        return success

    def _create_single_group(
        self, group_name: str, permission_codenames: List[str]
    ) -> bool:
        """Create single group with permissions"""
        try:
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created group: {group_name}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"ℹ Group already exists: {group_name}")
                )

            permissions: List[Permission] = []
            for perm_code in permission_codenames:
                perm = self._get_single_permission(perm_code)
                if perm:
                    permissions.append(perm)
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Found permission: {perm_code}")
                    )
                else:
                    self.stderr.write(
                        self.style.ERROR(f"✗ Permission not found: {perm_code}")
                    )
                    return False

            group.permissions.set(permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Group '{group_name}' got {len(permissions)} permissions: "
                    f"{', '.join([p.codename for p in permissions])}"
                )
            )

            return True

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"✗ Error creating group '{group_name}': {str(e)}")
            )
            return False

    def _get_single_permission(self, perm_code: str) -> Optional[Permission]:
        """Retrieve single permission with proper handling for custom permissions"""
        try:
            if "." in perm_code:
                app_label, codename = perm_code.split(".", 1)

                if codename == "view_advertisement_stats":
                    content_type = ContentType.objects.get(
                        app_label="advertisements", model="advertisement"
                    )
                    return Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                else:
                    if not ContentType.objects.filter(app_label=app_label).exists():
                        raise ValueError(f"App '{app_label}' doesn't exist")

                    return Permission.objects.get(
                        content_type__app_label=app_label, codename=codename
                    )
            else:
                return Permission.objects.get(codename=perm_code)

        except Permission.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Permission not found: '{perm_code}'"))
            return None
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error processing '{perm_code}': {str(e)}")
            )
            return None

    def add_arguments(self, parser: CommandParser) -> None:
        """Optional arguments for the command"""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate without actually creating anything",
        )
