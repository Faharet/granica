from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create 'manager' and 'submitter' groups and assign FormResponse permissions"

    def handle(self, *args, **options):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        try:
            from platform_manager.models import FormResponse
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Couldn't import FormResponse: {e}"))
            return

        ct = ContentType.objects.get_for_model(FormResponse)

        # manager -> view/change/delete
        manager_group, _ = Group.objects.get_or_create(name='manager')
        perms_manager = Permission.objects.filter(content_type=ct, codename__in=['view_formresponse', 'change_formresponse', 'delete_formresponse'])
        for p in perms_manager:
            manager_group.permissions.add(p)

        # submitter -> add only
        submitter_group, _ = Group.objects.get_or_create(name='submitter')
        perm_add = Permission.objects.filter(content_type=ct, codename='add_formresponse')
        for p in perm_add:
            submitter_group.permissions.add(p)

        self.stdout.write(self.style.SUCCESS('Groups and permissions ensured: manager, submitter'))
