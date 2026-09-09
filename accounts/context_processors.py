from .models import PagePermission 
 
 
def sidebar_permissions(request): 
 
    can_view_dashboard = False 
    can_view_users = False 
    can_view_roles = False 
    can_view_permissions = False 
    can_view_modules = False 
    can_view_audit_log = False 
 
    if request.user.is_authenticated: 
 
        if request.user.is_superuser: 
 
            can_view_dashboard = True 
            can_view_users = True 
            can_view_roles = True 
            can_view_permissions = True 
            can_view_modules = True 
            can_view_audit_log = True 
 
        elif request.user.role: 
 
            role = request.user.role 
 
            can_view_dashboard = PagePermission.objects.filter( 
                roles=role, 
                url_name='dashboard' 
            ).exists() 
 
            can_view_users = PagePermission.objects.filter( 
                roles=role, 
                url_name='user_view' 
            ).exists() 
 
            can_view_roles = PagePermission.objects.filter( 
                roles=role, 
                url_name='role_view' 
            ).exists() 
 
            can_view_permissions = PagePermission.objects.filter( 
                roles=role, 
                url_name='permission_management' 
            ).exists() 
 
            can_view_modules = PagePermission.objects.filter( 
                roles=role, 
                url_name='module_view' 
            ).exists() 

            can_view_audit_log = PagePermission.objects.filter( 
                roles=role, 
                url_name='audit_log_view' 
            ).exists() 
 
    return { 
        'can_view_dashboard': can_view_dashboard, 
        'can_view_users': can_view_users, 
        'can_view_roles': can_view_roles, 
        'can_view_permissions': can_view_permissions, 
        'can_view_modules': can_view_modules, 
        'can_view_audit_log': can_view_audit_log, 
    }