from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from auditlog.models import LogEntry
import json
import ast
from .decorators import role_required
from .models import Role, PagePermission, CustomUser, PermissionModule
from .forms import (UserCreateForm, UserEditForm,PagePermissionForm,PermissionModuleForm,)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'accounts/login.html', {
            'error': 'Email or password is incorrect'
        })
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@role_required('dashboard')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
@role_required('role_view')
def role_management(request):
    roles = Role.objects.all()
    paginator = Paginator(roles, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.user.is_superuser:
        can_create = True
        can_edit = True
        can_delete = True
    else:
        role = request.user.role
        can_create = PagePermission.objects.filter(
            roles=role,
            url_name='role_create'
        ).exists()
        can_edit = PagePermission.objects.filter(
            roles=role,
            url_name='role_edit'
        ).exists()
        can_delete = PagePermission.objects.filter(
            roles=role,
            url_name='role_delete'
        ).exists()
    if request.method == 'POST':
        if not request.user.is_superuser and not can_create:
            raise PermissionDenied
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            Role.objects.create(
                name=name,
                description=description
            )
        return redirect('role_management')
    
    query_params = request.GET.copy()
    query_params.pop('page', None)
    return render(request, 'accounts/role_management.html', {
    'roles': roles,
    'can_create': can_create,
    'can_edit': can_edit,
    'can_delete': can_delete,
    'page_obj': page_obj,
    'query_params': query_params.urlencode(),
})

@login_required
@role_required('role_delete')
def role_delete(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        role.delete()
    return redirect('role_management')


@login_required
@role_required('role_edit')
def role_edit(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            role.name = name
            role.description = description
            role.save()
            return redirect('role_management')

@login_required
@role_required('permission_management')
def permission_management(request):
    roles = Role.objects.all()
    permissions = PagePermission.objects.select_related(
        'module'
    ).all()
    selected_role = None
    selected_permissions = []

    role_id = request.GET.get('role')


    # =============================== Selected Role ===============================

    if role_id:

        selected_role = get_object_or_404(
            Role,
            id=role_id
        )
        selected_permissions = list(
            selected_role.page_permissions.values_list(
                'id',
                flat=True
            )
        )
    if request.user.is_superuser:
        can_permission_create = True
        can_permission_edit = True
        can_permission_delete = True
    else:
        role = request.user.role
        can_permission_create = PagePermission.objects.filter(
            roles=role,
            url_name='permission_create'
        ).exists()
        can_permission_edit = PagePermission.objects.filter(
            roles=role,
            url_name='permission_edit'
        ).exists()
        can_permission_delete = PagePermission.objects.filter(
            roles=role,
            url_name='permission_delete'
        ).exists()
    if (
        request.method == 'POST'
        and request.POST.get('action') == 'create_permission'
    ):
        if not can_permission_create:
            raise PermissionDenied
        permission_form = PagePermissionForm(
            request.POST
        )
        if permission_form.is_valid():
            permission_form.save()
            return JsonResponse({
                'success': True,
                'message': 'Permission created successfully.',
            })
        return JsonResponse({
            'success': False,
            'errors': permission_form.errors.get_json_data(),
        }, status=400)
    if (
        request.method == 'POST'
        and request.POST.get('action') == 'assign_permissions'
    ):
        role_id = request.POST.get('role_id')
        selected_role = get_object_or_404(
            Role,
            id=role_id
        )
        permission_ids = request.POST.getlist(
            'permissions'
        )
        selected_role.page_permissions.set(
            permission_ids
        )
        return redirect(
            f'{reverse("permission_management")}?role={selected_role.id}'
        )
    permission_form = PagePermissionForm()
    return render(
        request,
        'accounts/permission_management.html',
        {
            'roles': roles,
            'permissions': permissions,
            'selected_role': selected_role,
            'selected_permissions': selected_permissions,
            'permission_form': permission_form,

            'can_permission_create': can_permission_create,
            'can_permission_edit': can_permission_edit,
            'can_permission_delete': can_permission_delete,
        }
    )
@login_required
@role_required('permission_edit')
def permission_edit(request, permission_id):
    permission = get_object_or_404(
        PagePermission,
        id=permission_id
    )

    if request.method != 'POST':
        return redirect('permission_management')

    form = PagePermissionForm(
        request.POST,
        instance=permission
    )

    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

        return redirect('permission_management')

    form.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Permission updated successfully.',
        })

    return redirect('permission_management')


@login_required
@role_required('permission_delete')
def permission_delete(request, permission_id):
    permission = get_object_or_404(
        PagePermission,
        id=permission_id
    )

    if request.method == 'POST':
        permission.delete()

    return redirect('permission_management')


@login_required
@role_required('user_view')
def user_list(request):
    users = CustomUser.objects.select_related('role').all()
    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    create_form = UserCreateForm()
    users_with_forms = []

    if request.user.is_superuser:
        can_create = True
        can_edit = True
        can_delete = True
    else:
        role = request.user.role
        can_create = PagePermission.objects.filter(
            roles=role,
            url_name='user_create'
        ).exists()
        can_edit = PagePermission.objects.filter(
            roles=role,
            url_name='user_edit'
        ).exists()
        can_delete = PagePermission.objects.filter(
            roles=role,
            url_name='user_delete'
        ).exists()
    for user in page_obj:
        edit_form = UserEditForm(
            initial={
                'username': user.username,
                'role': user.role,
                'is_active': user.is_active,
            },
            user_id=user.id
        )
        users_with_forms.append({
            'user': user,
            'edit_form': edit_form,
        })

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'accounts/user_list.html', {
    'users': users,
    'create_form': create_form,
    'users_with_forms': users_with_forms,
    'can_create': can_create,
    'can_edit': can_edit,
    'can_delete': can_delete,
    'page_obj': page_obj,
    'query_params': query_params.urlencode(),
})

@login_required
@role_required('user_create')
def user_create(request):
    if request.method != 'POST':
        return redirect('user_list')
    form = UserCreateForm(request.POST)
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)
        return render(request, 'accounts/user_create.html', {
            'form': form
        })
    CustomUser.objects.create_user(
        email=form.cleaned_data['email'],
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password'],
        role=form.cleaned_data['role']
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'redirect': reverse('user_list'),
        })
    return redirect('user_list')

@login_required
@role_required('user_edit')
def user_edit(request, user_id):
    user_obj = get_object_or_404(
        CustomUser,
        id=user_id
    )
    if request.method != 'POST':
        return redirect('user_list')
    form = UserEditForm(
        request.POST,
        user_id=user_obj.id
    )
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)
    user_obj.username = form.cleaned_data['username']
    user_obj.role = form.cleaned_data['role']
    user_obj.is_active = form.cleaned_data['is_active']
    user_obj.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'redirect': reverse('user_list'),
        })
    return redirect('user_list')


@login_required
@role_required('user_delete')
def user_delete(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        if user_obj == request.user:
            return redirect('user_list')
        user_obj.delete()
        return redirect('user_list')
    return redirect('user_list')

@login_required
@role_required('module_view')
def module_management(request):
    modules = PermissionModule.objects.all().order_by('name')
    if request.user.is_superuser:
        can_create = True
        can_edit = True
        can_delete = True
    else:
        role = request.user.role
        can_create = PagePermission.objects.filter(
            roles=role,
            url_name='module_create'
        ).exists()
        can_edit = PagePermission.objects.filter(
            roles=role,
            url_name='module_edit'
        ).exists()
        can_delete = PagePermission.objects.filter(
            roles=role,
            url_name='module_delete'
        ).exists()
    if (
        request.method == 'POST'
        and request.POST.get('action') == 'create_module'
    ):
        if not can_create:
            raise PermissionDenied
        form = PermissionModuleForm(
            request.POST
        )
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Module created successfully.',
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)
    return render(
        request,
        'accounts/module_management.html',
        {
            'modules': modules,
            'module_form': PermissionModuleForm(),
            'can_create': can_create,
            'can_edit': can_edit,
            'can_delete': can_delete,
        }
    )


@login_required
@role_required('module_edit')
def module_edit(request, module_id):
    module = get_object_or_404(
        PermissionModule,
        id=module_id
    )
    if request.method != 'POST':
        return redirect('module_management')
    form = PermissionModuleForm(
        request.POST,
        instance=module
    )
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)
        return redirect('module_management')
    form.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Module updated successfully.',
        })
    return redirect('module_management')

@login_required
@role_required('module_delete')
def module_delete(request, module_id):
    module = get_object_or_404(
        PermissionModule,
        id=module_id
    )
    if request.method == 'POST':
        module.delete()
    return redirect('module_management')

SENSITIVE_FIELDS = {'password'}
@login_required
@role_required('audit_log_view')
def audit_log_view(request):
    logs = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    for log in page_obj:
        raw = log.changes
        changes_dict = {}
        if isinstance(raw, dict):
            changes_dict = raw
        elif raw:
            try:
                changes_dict = json.loads(raw)
            except (ValueError, TypeError):
                try:
                    changes_dict = ast.literal_eval(raw)
                except (ValueError, SyntaxError):
                    changes_dict = {}
        parsed = []
        for field, values in changes_dict.items():
            # ================= M2M field changes =================
            if isinstance(values, dict) and values.get('type') == 'm2m':
                operation = values.get('operation', 'changed')
                objects = values.get('objects', [])
                objects_str = ', '.join(str(o) for o in objects) if objects else '—'
                parsed.append({
                    'field': field,
                    'old': operation,
                    'new': objects_str,
                })
                continue
            # ================= Regular fields =================
            if isinstance(values, (list, tuple)):
                old_raw = values[0] if len(values) > 0 else None
                new_raw = values[1] if len(values) > 1 else None
            else:
                old_raw = None
                new_raw = values
            if field.lower() in SENSITIVE_FIELDS:
                old_val = '........' if old_raw not in (None, 'None') else '—'
                new_val = '........' if new_raw not in (None, 'None') else ''
            else:
                old_val = old_raw if old_raw not in (None, 'None') else '—'
                new_val = new_raw if new_raw is not None else ''
            parsed.append({
                'field': field,
                'old': old_val,
                'new': new_val,
            })
        log.parsed_changes = parsed
        log.changes_element_id = f'log-changes-{log.pk}'
    query_params = request.GET.copy()
    query_params.pop('page', None)
    return render(request, 'accounts/audit_log.html', {
        'page_obj': page_obj,
        'query_params': query_params.urlencode(),
        'action_choices': LogEntry.Action.choices,
        'selected_action': action_filter,
    })