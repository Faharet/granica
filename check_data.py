import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'granica_admin.settings')
django.setup()

from platform_manager.models import FormResponse

print("Checking first 5 responses:\n")
for r in FormResponse.objects.all()[:5]:
    print(f"ID: {str(r.id)[:8]}...")
    print(f"  last_name: '{r.last_name}'")
    print(f"  first_name: '{r.first_name}'")
    print(f"  patronymic: '{r.patronymic}'")
    print(f"  full_name_and_birth: '{r.full_name_and_birth[:50] if r.full_name_and_birth else ''}'...")
    print("=" * 50)
