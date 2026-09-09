from django.urls import path
from .views import login_view,logout_view,dashboard,role_management,role_delete, role_edit ,permission_management, user_delete , user_list, user_create, user_edit,permission_edit,permission_delete,module_management,module_edit,module_delete,audit_log_view
urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('super-admin/roles/', role_management, name='role_management'),
    path('super-admin/roles/delete/<int:role_id>/', role_delete, name='role_delete'),
    path('super-admin/roles/edit/<int:role_id>/', role_edit, name='role_edit'),
    path('super-admin/permissions/',permission_management,name='permission_management'),
    path('super-admin/users/', user_list, name='user_list'),
    path('super-admin/users/create/', user_create, name='user_create'),
    path('super-admin/users/edit/<int:user_id>/', user_edit, name='user_edit'),
    path('super-admin/users/delete/<int:user_id>/', user_delete, name='user_delete'),
    path('super-admin/permissions/edit/<int:permission_id>/',permission_edit,name='permission_edit'),
    path('super-admin/permissions/delete/<int:permission_id>/',permission_delete,name='permission_delete'),
    path('super-admin/modules/',module_management,name='module_management'),
    path('super-admin/modules/edit/<int:module_id>/',module_edit,name='module_edit'),
    path('super-admin/modules/delete/<int:module_id>/',module_delete,name='module_delete'),
    path('super-admin/audit-log/', audit_log_view, name='audit_log_view'),
]