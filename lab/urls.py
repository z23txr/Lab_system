from django.urls import path
from .views import (
    lab_management,
    lab_create,
    lab_edit,
    lab_delete,
    designation_management,
    designation_create,
    designation_edit,
    designation_delete,
)

urlpatterns = [
    path('labs/', lab_management, name='lab_management'),
    path('labs/create/', lab_create, name='lab_create'),
    path('labs/edit/<int:lab_id>/', lab_edit, name='lab_edit'),
    path('labs/delete/<int:lab_id>/', lab_delete, name='lab_delete'),

    path('designations/', designation_management, name='designation_management'),
    path('designations/create/', designation_create, name='designation_create'),
    path('designations/edit/<int:designation_id>/', designation_edit, name='designation_edit'),
    path('designations/delete/<int:designation_id>/', designation_delete, name='designation_delete'),
]