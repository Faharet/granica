from django.shortcuts import redirect
from django.urls import reverse


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
