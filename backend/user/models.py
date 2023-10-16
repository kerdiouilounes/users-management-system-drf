from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import FieldDoesNotExist


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_validated_user_data):
        user = self.model(email=email, password=password, **extra_validated_user_data)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        validated_superuser_data = self.create_validated_superuser_data(email, password, **extra_fields)
        return self.create_user(**validated_superuser_data)
    
    def create_staff(self, email, password, **extra_fields):
        validated_staff_data = self.create_validated_staff_data(email, password, **extra_fields)
        return self.create_user(**validated_staff_data)
    
    def create_consumer(self, email, password, **extra_fields):
        validated_consumer_data = self.create_validated_consumer_data(email, password, **extra_fields)
        return self.create_user(**validated_consumer_data)


    def create_validated_user_data(self, email, password, **extra_fields):
        if not email:
            raise FieldDoesNotExist('The Email field must be set')
        if not password:
            raise FieldDoesNotExist('The Password field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        return {'email' : user.email, 'password' : user.password, **extra_fields}

    def create_validated_superuser_data(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_validated_user_data(email, password, **extra_fields)
    
    def create_validated_staff_data(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is True:
            raise ValueError('Staff must have is_superuser=False.')

        return self.create_validated_user_data(email, password, **extra_fields)
    
    def create_validated_consumer_data(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if extra_fields.get('is_staff') is True:
            raise ValueError('Consumer must have is_staff=False.')
        if extra_fields.get('is_superuser') is True:
            raise ValueError('Consumer must have is_superuser=False.')

        return self.create_validated_user_data(email, password, **extra_fields)
    
    def filter_users(self, **filters):
        return self.filter(**filters)
    
    def get_consumer_users(self):
        return self.filter_users(is_staff=False, is_superuser=False)

    def get_staff_users(self):
        return self.filter_users(is_staff=True, is_superuser=False)

    def get_superusers(self):
        return self.filter_users(is_superuser=True)
    
    def get_user_by_pk(self, pk):
        user = None
        try:
            user = self.get(pk=pk)
        except Exception:
            pass
        return user
    


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    @property
    def is_consumer(self):
        return not (self.is_staff and self.is_superuser)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __str__(self):
        return self.email
