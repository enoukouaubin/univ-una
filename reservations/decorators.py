from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from reservations.models import Administrateur

def admin_required(view_func):
    def check_admin(user):
        if user.is_authenticated:
            try:
                admin = Administrateur.objects.get(email=user.email)
                return admin.role in ['super_admin', 'admin'] and admin.statut == 'actif'
            except Administrateur.DoesNotExist:
                return False
        return False
    
    decorated_view = user_passes_test(check_admin, login_url='reservations:login')(view_func)
    return decorated_view