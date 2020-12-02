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
        user = self.create_user(email, password, lastname, firstname, **extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, DirtyFieldsMixin):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    # note that the default character numbers must be less than or 100
    # add https: // res.cloudinary.com / dnrh79klc + /image/path
    email = models.EmailField(
        max_length=50,
        unique=True,
        error_messages={"unique": "A user with this email already exists"},
    )
    email_verified = models.BooleanField(default=False)
    password = models.CharField(
        max_length=128, validators=[password_validation.validate_password]
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    # ensure this is objects and not object
    # else User.objects.all() won't work
    # it has to be Class.object.all()
    # and most 3rd party packages depend on objects
    objects = UserManager()

    REQUIRED_FIELDS = ["firstname", "lastname", "password"]
    USERNAME_FIELD = "email"

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

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
        self.image = value

    @property
    def is_staff(self):
        return self.is_admin
