from django.apps import AppConfig


class PlatformManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform_manager'
    verbose_name = "Панель управления"
    icon = 'fa fa-square-poll-vertical'
    navigation_path = 'platform_manager.navigation.get_menu_items'
    
    def ready(self):
        # Create standard groups if they don't exist. If migrations haven't run yet,
        # some models/permissions may not be available; ignore failures silently.
        try:
            from django.contrib.auth.models import Group, Permission
            from django.contrib.contenttypes.models import ContentType
            from .models import FormResponse

            ct = ContentType.objects.get_for_model(FormResponse)

            # manager -> view and change permissions
            manager_group, _ = Group.objects.get_or_create(name='manager')
            perms = Permission.objects.filter(content_type=ct, codename__in=['view_formresponse', 'change_formresponse', 'delete_formresponse'])
            for p in perms:
                manager_group.permissions.add(p)

            # submitter -> add permission only
            submitter_group, _ = Group.objects.get_or_create(name='submitter')
            add_perm = Permission.objects.filter(content_type=ct, codename='add_formresponse')
            for p in add_perm:
                submitter_group.permissions.add(p)
        except Exception:
            # It's ok to fail here during migrate/initial setup — permissions may not exist yet.
            pass
        # Connect a signal so we can flag sessions after successful login.
        try:
            from django.contrib.auth.signals import user_logged_in

            def _on_user_logged_in(sender, user, request, **kwargs):
                # Flag the session so middleware can redirect on next request.
                try:
                    if user.groups.filter(name__in=['manager', 'submitter']).exists():
                        request.session['redirect_to_panel'] = True
                except Exception:
                    # If anything goes wrong (e.g., during migrations), ignore.
                    pass

            user_logged_in.connect(_on_user_logged_in)
        except Exception:
            # Safety: don't break startup if signals aren't available.
            pass