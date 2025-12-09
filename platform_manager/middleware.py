from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.utils.translation import gettext as _


class PanelRedirectMiddleware:
    """Redirect users in manager/submitter groups to the panel after login.

    Workflow:
    - A signal handler sets `request.session['redirect_to_panel'] = True` on login.
    - Middleware runs on the next request and performs the redirect once.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            should = request.session.pop('redirect_to_panel', False)
        except Exception:
            should = False

        if should and request.user.is_authenticated:
            # Only redirect managers and submitters
            if request.user.groups.filter(name__in=['manager', 'submitter']).exists():
                # Avoid redirect loops if already on panel
                panel_url = reverse('manager_panel')
                if request.path != panel_url:
                    return redirect(panel_url)

        return self.get_response(request)


class RestrictAdminAccessMiddleware:
    """Block admin access for non-superuser staff members (managers/submitters).
    
    Only superusers can access the admin panel.
    Managers and submitters are redirected to their panel.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if trying to access admin
        if request.path.startswith('/admin/') or request.path.startswith('/ru/admin/') or request.path.startswith('/kk/admin/') or request.path.startswith('/en/admin/'):
            if request.user.is_authenticated:
                # Allow only superusers
                if not request.user.is_superuser:
                    # Redirect managers/submitters to their panel
                    if request.user.groups.filter(name__in=['manager', 'submitter']).exists():
                        return redirect('manager_panel')
                    # Block other non-superuser staff
                    return HttpResponseForbidden(
                        f"<h1>{_('Access Denied')}</h1>"
                        f"<p>{_('You do not have permission to access the admin panel.')}</p>"
                        f"<p><a href='/panel/'>{_('Go to Panel')}</a></p>"
                    )

        return self.get_response(request)
