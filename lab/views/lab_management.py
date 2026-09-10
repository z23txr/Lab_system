from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.decorators import role_required
from ..models import Lab, Designation
from ..forms import LabForm, DesignationForm


# =============================== Lab ===============================

@login_required
@role_required('lab_view')
def lab_management(request):
    labs = Lab.objects.all().order_by('name')
    form = LabForm()

    return render(request, 'lab/lab_management/lab_management.html', {
        'labs': labs,
        'form': form,
    })


@login_required
@role_required('lab_create')
def lab_create(request):
    if request.method != 'POST':
        return redirect('lab_management')

    form = LabForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Lab created successfully.',
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors.get_json_data(),
    }, status=400)


@login_required
@role_required('lab_edit')
def lab_edit(request, lab_id):
    lab = get_object_or_404(Lab, id=lab_id)

    if request.method != 'POST':
        return redirect('lab_management')

    form = LabForm(request.POST, instance=lab)
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

    form.save()
    return JsonResponse({
        'success': True,
        'message': 'Lab updated successfully.',
    })


@login_required
@role_required('lab_delete')
def lab_delete(request, lab_id):
    lab = get_object_or_404(Lab, id=lab_id)
    if request.method == 'POST':
        lab.delete()
    return redirect('lab_management')


# =============================== Designation ===============================

@login_required
@role_required('designation_view')
def designation_management(request):
    designations = Designation.objects.all().order_by('name')
    form = DesignationForm()

    return render(request, 'lab/lab_management/designation_management.html', {
        'designations': designations,
        'form': form,
    })


@login_required
@role_required('designation_create')
def designation_create(request):
    if request.method != 'POST':
        return redirect('designation_management')

    form = DesignationForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Designation created successfully.',
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors.get_json_data(),
    }, status=400)


@login_required
@role_required('designation_edit')
def designation_edit(request, designation_id):
    designation = get_object_or_404(Designation, id=designation_id)

    if request.method != 'POST':
        return redirect('designation_management')

    form = DesignationForm(request.POST, instance=designation)
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

    form.save()
    return JsonResponse({
        'success': True,
        'message': 'Designation updated successfully.',
    })


@login_required
@role_required('designation_delete')
def designation_delete(request, designation_id):
    designation = get_object_or_404(Designation, id=designation_id)
    if request.method == 'POST':
        designation.delete()
    return redirect('designation_management')