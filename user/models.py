from __future__ import absolute_import

from dirtyfields import DirtyFieldsMixin
from django.contrib.auth import password_validation
from django.contrib.auth.models import (
    AbstractBaseUser,
    AbstractUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from paytime.utils import validate_ng_mobile_number


class UserManager(BaseUserManager):
    def create_user(self, email, password, lastname, firstname, **extrafields):
        if not email:
            ValueError("Email field is required")
        if not firstname:
            ValueError("Firstname field is required")
        if not lastname:
            ValueError("Lastname field is required")

        user = self.model(
            email=self.normalize_email(email),
            password=password,
            firstname=firstname,
            lastname=lastname,
            **extrafields
        )

        user.is_active = True
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, lastname, firstname, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(email, password, lastname, firstname, **extra_fields)
        user.is_admin = True
        # used by the PermissionsMixin to
        # grant all permissions
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(DirtyFieldsMixin, AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(
        max_length=50,
        unique=True,
        error_messages={"unique": "A user with this email already exists"},
    )
    date_of_birth = models.DateField(null=True, blank=True)
    password = models.CharField(
        max_length=128, validators=[password_validation.validate_password]
    )
    mobile = models.CharField(
        max_length=20, blank=True, null=True, validators=[validate_ng_mobile_number]
    )
    address1 = models.CharField(max_length=30, blank=True, null=True)
    area = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(
        blank=True, null=True, upload_to="profile_pictures"
    )
    gender = models.CharField(max_length=6, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    # we need to replace with is_staff
    is_admin = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    # ensure this is objects and not object
    # else User.objects.all() won't work
    # it has to be Model.objects.all()
    # and most 3rd party packages depend on objects
    objects = UserManager()

    REQUIRED_FIELDS = ["firstname", "lastname", "password"]
    USERNAME_FIELD = "email"

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

    def save(self, *args, **kwargs):
        self.firstname = self.firstname.title().strip()
        self.lastname = self.lastname.title().strip()
        return super(User, self).save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_username(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.firstname, self.lastname)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.firstname

    # allows assignment property to the image value
    # from the view
    def __setitem__(self, key, value):
        self.profile_picture = value

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def has_active_investment(self):
        return self.investment_set.filter(status__in=["active", "pending"]).exists()

    def get_user_messages(self):
        return self.messages.all().order_by("read", "-created_at")[0:4]

    @property
    def total_unread_messages(self):
        return self.messages.filter(read=False).count()


class Document(DirtyFieldsMixin, models.Model):
    type = models.CharField(max_length=30)
    file = models.FileField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    verified = models.BooleanField(default=False)
