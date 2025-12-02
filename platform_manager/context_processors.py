from django.urls import reverse

def menu_items(request):
    """Add custom menu items to the admin template context."""
    items = []
    
    if request.user.is_authenticated:
        items.append({
            'title': 'Формы',
            'icon': 'fa-solid fa-file-pen',
            'children': [
                {
                    'title': 'Отправить форму',
                    'url': reverse('platform_manager:form_submit'),
                },
            ]
        })
        
        # Добавляем пункт меню "Просмотр ответов" только для менеджеров
        if request.user.groups.filter(name='manager').exists():
            items[0]['children'].append({
                'title': 'Просмотр ответов',
                'url': reverse('platform_manager:form_responses'),
            })
    
    is_manager = False
    try:
        is_manager = request.user.is_authenticated and request.user.groups.filter(name='manager').exists()
    except Exception:
        is_manager = False

    return {
        'custom_menu_items': items,
        'is_manager': is_manager,
    }