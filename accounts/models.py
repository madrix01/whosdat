from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class UserManager(BaseUserManager):
    def create_user(self, admn_no, email, password=None):
        user = self.model(email=email, admn_no=admn_no)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, admn_no, email, password=None):
        user = self.create_user(admn_no, email, password=password,)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, null=True)
    admn_no = models.CharField(max_length=8, unique=True)
    admin = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timepost = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'admn_no'
    REQUIRED_FIELDS = ['email']

    def __str__(self, *args, **kwargs):
        return self.email

    def __str__(self, *args, **kwargs):
        return self.admn_no

    def has_perm(self, perm, obj=None, *args, **kwargs):
        return True
    
    def has_module_perms(self, app_label, *args, **kwargs):
        return True

    @property
    def is_admin(self, *args, **kwargs):
        return self.admin

    @property
    def is_staff(self, *args, **kwargs):
        return self.staff

    @property
    def is_active(self, *args, **kwargs):
        return self.active