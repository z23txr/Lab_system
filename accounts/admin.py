from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role , PagePermission

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email', 'username')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(PagePermission)

