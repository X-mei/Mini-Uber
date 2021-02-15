from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _


# Create your models here.

class VehicleInfo(models.Model):
    first_name = models.CharField(max_length=20, blank=False)
    last_name = models.CharField(max_length=20, blank=False)
    vehicle_type = models.CharField(max_length=30, blank=False)
    license_number = models.CharField(max_length=30, blank=False)
    # The passengers should be a field between 1 - 50.
    n_passengers = models.IntegerField(validators=[
        MaxValueValidator(50),
        MinValueValidator(1),
    ], blank=False)
    special_info = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.vehicle_type

    def get_message(self):
        return "First name: " + self.first_name + "\n" + "Last name: " + self.last_name + "\n" + "Vehicle type: " + self.vehicle_type + "\n" + "License number: " + self.license_number + "\n" + "Seats: " + str(self.n_passengers) + "\n" + "Special info: " + self.special_info + "\n"


# Reference: https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **other_fields):
        """
        Create and save a user.
        All fields required.
        """
        if not username or not email:
            raise ValueError(_('The email and username must be set.'))
        email = self.normalize_email(email)

        user = self.model(username=username, email=email, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(_('superuser should have staff permission.'))
        if other_fields.get('is_superuser') is not True:
            raise ValueError(_('superuser should have superuser permission.'))
        if other_fields.get('is_active') is not True:
            raise ValueError(_('superuser should have active permission.'))
        return self.create_user(username, email, password, **other_fields)


class User(AbstractBaseUser):
    """
    A customized user model designed for this project.
    Every User should have three fields: username, email, password.
    """
    username = models.CharField(max_length=40, unique=True, blank=False)
    email = models.EmailField(_('email address'), blank=False, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_driver = models.BooleanField(default=False)
    # The user can access its license by using user.driver_license
    driver_license = models.OneToOneField(VehicleInfo, on_delete=models.CASCADE, blank=True, null=True)
    # The user can access its shared rides by
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username


class RideManager(models.Manager):
    """
    A customized manager class which is used to return some useful queryset.
    """

    def owned_ride_for(self, user):
        return self.filter(
            ride_status='OP',
            owner=user,
        ) | self.filter(
            ride_status='CF',
            owner=user,
        )


class Ride(models.Model):
    """
    This class represents the ride that can be owned by the user.
    One user can have multiple rides while a ride can owned by only one user.
    """

    class RideStatus(models.TextChoices):
        OPEN = 'OP'
        CONFIRMED = 'CF'
        COMPLETED = 'CL'

    destination_addr = models.CharField(max_length=50, blank=False)
    arrival_time = models.DateTimeField(blank=False)
    passengers = models.IntegerField(validators=[
        MaxValueValidator(50),
        MinValueValidator(1),
    ], blank=False)
    ride_status = models.CharField(
        max_length=2,
        choices=RideStatus.choices,
        blank=False,
        default=RideStatus.OPEN,
    )
    can_be_shared = models.BooleanField(
        blank=False,
    )
    # Access using user.owned_rides to access all the rides owned by the user.
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="owned_rides",
    )
    # ride.sharer.add(User) ...
    # Access using user.shared_rides to access all the rides that the user shared.
    sharer = models.ManyToManyField(
        User,
        related_name="shared_rides",
    )
    vehicle_type = models.CharField(
        blank=True,
        max_length=30,
    )
    special_request = models.CharField(
        blank=True,
        max_length=200
    )
    # Access using user.driver_rides to access all the rides that the user act as driver
    driver = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="driver_rides",
    )
    objects = RideManager()

    def can_be_edited(self):
        return self.ride_status != 'CL'

    def get_message(self):
        return "Destination:" + self.destination_addr + "\n" + "Arrival time:" + self.arrival_time.strftime("%m/%d/%Y, %H:%M:%S") + "\n" + "passengers:" + str(self.passengers) + "\n" + "vehicle type:" + self.vehicle_type + "\n" + "special info:" + self.special_request + "\n"
