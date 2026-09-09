from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from auditlog.registry import auditlog

# ================Permission Module========================
class PermissionModule(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# ===============================Role Model========================
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# ===============================Page Permission Model========================
class PagePermission(models.Model):
    module = models.ForeignKey(
    PermissionModule,
    on_delete=models.CASCADE,
    related_name='permissions',
    null=True,
    blank=True
)
    name = models.CharField(max_length=100, unique=True)
    url_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    roles = models.ManyToManyField(
        Role,
        related_name='page_permissions',
        blank=True
    )
    def __str__(self):
        return self.name
# ===============================Custom User Manager========================
class CustomUserManager(BaseUserManager):

    def create_user(self,email,username,password=None,**extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        email=self.normalize_email(email)
        user=self.model(email=email,username=username,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,username,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(email,username,password,**extra_fields)

# ===============================Custom User Model========================
class CustomUser(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True)
    username=models.CharField(max_length=30,unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    objects=CustomUserManager()
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
    def __str__(self):
        return self.email

auditlog.register(Role, m2m_fields={'page_permissions'})
auditlog.register(PagePermission)
auditlog.register(PermissionModule)
auditlog.register(CustomUser)