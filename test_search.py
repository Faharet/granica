import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'granica_admin.settings')
django.setup()

from platform_manager.models import FormResponse
from django.db.models import Q

# Test multi-variant search
search_terms_to_test = ["фархад", "ФАРХАД", "Фархад", "мұханғалиев", "МҰХАНҒАЛИЕВ"]

print("Testing multi-variant search:")
print("-" * 60)

for search_term in search_terms_to_test:
    # Generate variants like in the code
    search_variants = [
        search_term,
        search_term.lower(),
        search_term.upper(),
        search_term.capitalize(),
        search_term.title()
    ]
    
    q_objects = Q()
    for variant in search_variants:
        q_objects |= (
            Q(last_name__contains=variant) |
            Q(first_name__contains=variant) |
            Q(patronymic__contains=variant) |
            Q(full_name_and_birth__contains=variant)
        )
    
    results = FormResponse.objects.filter(q_objects)
    print(f"Search '{search_term}': {results.count()} results")
    for r in results:
        print(f"  → {r.last_name} {r.first_name}")




