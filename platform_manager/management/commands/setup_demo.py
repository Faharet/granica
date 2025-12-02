from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from platform_manager.models import FormResponse

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates demo users and sample data for the application'

    def handle(self, *args, **kwargs):
        # Create groups if they don't exist
        manager_group, _ = Group.objects.get_or_create(name='manager')
        submitter_group, _ = Group.objects.get_or_create(name='submitter')

        # Create demo users
        admin_user = User.objects.create_superuser(
            username='admins',
            password='admin',
            phone='+77077682478',
            email='admins@example.com'
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin user: admin/admin'))

        manager_user = User.objects.create_user(
            username='managers',
            password='manager',
            phone='+77777777788',
            email='managers@example.com'
        )
        manager_user.groups.add(manager_group)
        self.stdout.write(self.style.SUCCESS(f'Created manager user: manager/manager'))

        submitter_user = User.objects.create_user(
            username='submitters',
            password='submitter',
            phone='+77777777779',
            email='submitters@example.com'
        )
        submitter_user.groups.add(submitter_group)
        self.stdout.write(self.style.SUCCESS(f'Created submitter user: submitter/submitter'))

        # Create some sample form responses
        FormResponse.objects.create(
            first_name='John',
            last_name='Doe',
            created_by=submitter_user
        )
        FormResponse.objects.create(
            first_name='Jane',
            last_name='Smith',
            created_by=submitter_user
        )
        self.stdout.write(self.style.SUCCESS('Created sample form responses'))

        self.stdout.write(self.style.SUCCESS('Demo setup completed!'))