from django import forms
from .models import Lab, Designation

INPUT_CLASSES = (
    "w-full px-3.5 py-2.5 border border-[#E0D4C6] rounded-xl "
    "bg-[#FDFCFB] text-sm text-[#2B2A2E] placeholder:text-[#7C6A5B]/50 "
    "focus:outline-none focus:ring-2 focus:ring-[#C7A37E]/30 "
    "focus:border-[#C7A37E] transition"
)


class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Name of Lab",
            }),
        }


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Name of Designation",
            }),
        }