from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

def get_menu_items(request):
    """Return menu items for the platform manager app."""
    items = []
    user = request.user

    # Basic form submission - available to all authenticated users
    if user.is_authenticated:
        items.append({
            'title': _('Submit Form'),
            'url': reverse_lazy('platform_manager:form_submit'),
            'icon': 'fa-solid fa-file-pen',
            'permissions': [],  # No special permissions needed
        })

    # Responses list - only for managers
    if user.groups.filter(name='manager').exists():
        items.append({
            'title': _('View Responses'),
            'url': reverse_lazy('platform_manager:form_responses'),
            'icon': 'fa-solid fa-list-check',
            'permissions': ['platform_manager.view_formresponse'],
        })

    return items