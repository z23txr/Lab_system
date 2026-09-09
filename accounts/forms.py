from django import forms
from .models import CustomUser, Role, PagePermission, PermissionModule

INPUT_CLASSES = (
    "w-full px-3.5 py-2.5 "
    "border border-[#E0D4C6] rounded-xl "
    "bg-[#FDFCFB] text-sm text-[#2B2A2E] "
    "placeholder:text-[#7C6A5B]/50 "
    "focus:outline-none focus:ring-2 "
    "focus:ring-[#C7A37E]/30 "
    "focus:border-[#C7A37E] "
    "transition"
)

class UserCreateForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "user@example.com",
                "autocomplete": "email",
            }
        )
    )
    username = forms.CharField(
        max_length=30,
        min_length=3,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "johndoe",
                "autocomplete": "username",
            }
        )
    )
    password = forms.CharField(
        min_length=8,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASSES + " pr-11",
                "placeholder": "••••••••",
                "autocomplete": "new-password",
            }
        )
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="Select a role",
        label="Role",
        widget=forms.Select(
            attrs={
                "class": INPUT_CLASSES,
            }
        )
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )
        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            raise forms.ValidationError(
                "Username is required."
            )
        if " " in username:
            raise forms.ValidationError(
                "Username cannot contain spaces."
            )
        if not username.replace("_", "").isalnum():
            raise forms.ValidationError(
                "Username can only contain letters, numbers and underscores."
            )
        if CustomUser.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not any(char.isupper() for char in password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not any(char.islower() for char in password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError(
                "Password must contain at least one number."
            )
        return password

class UserEditForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        min_length=3,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "johndoe",
                "autocomplete": "username",
            }
        )
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="Select a role",
        label="Role",
        widget=forms.Select(
            attrs={
                "class": INPUT_CLASSES,
            }
        )
    )
    is_active = forms.BooleanField(
        required=False,
        label="Active",
        widget=forms.CheckboxInput(
            attrs={
                "class": (
                    "h-4 w-4 rounded border-[#E0D4C6] "
                    "text-[#7C6A5B] "
                    "focus:ring-[#C7A37E]"
                )
            }
        )
    )
    def __init__(self, *args, user_id=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.user_id = user_id

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            raise forms.ValidationError(
                "Username is required."
            )
        if " " in username:
            raise forms.ValidationError(
                "Username cannot contain spaces."
            )
        if not username.replace("_", "").isalnum():
            raise forms.ValidationError(
                "Username can only contain letters, numbers and underscores."
            )
        existing_user = CustomUser.objects.filter(
            username__iexact=username
        )
        if self.user_id:
            existing_user = existing_user.exclude(
                id=self.user_id
            )
        if existing_user.exists():
            raise forms.ValidationError(
                "This username is already taken."
            )
        return username


class PagePermissionForm(forms.ModelForm):
    class Meta:
        model = PagePermission
        fields = ["module", "name", "url_name", "description"]
        widgets = {
            "module": forms.Select(attrs={
                "class": INPUT_CLASSES
            }),
            "name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "e.g. Create User",
            }),
            "url_name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "e.g. user_create",
            }),
            "description": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "What can this permission do?",
            }),
        }


class PermissionModuleForm(forms.ModelForm):

    class Meta:
        model = PermissionModule
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "e.g. User Management",
            }),
        }