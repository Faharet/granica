from django import setup
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','granica_admin.settings')
setup()
from platform_manager.models import FormResponse
qs = FormResponse.objects.order_by('-created_at')[:10]
for r in qs:
    print('ID:', r.id)
    print(' full_name_photo:', getattr(r.full_name_photo, 'name', None))
    print(' person_photo:', getattr(r.person_photo, 'name', None))
    print(' additional:', list(r.additional_photos.values_list('photo', flat=True)))
    print('---')
