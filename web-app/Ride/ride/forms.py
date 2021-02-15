from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from .models import VehicleInfo, User, Ride


def extract_edit_entry(d, key):
    """
    Extract edit entry within the dictionary d and deletes it.
    Return the value of edit entry.
    If it does not exist, return None.
    """
    if key not in d.keys():
        return None
    result = d[key]
    del d[key]
    return result


class UserForm(forms.ModelForm):
    """
    A form for user to register.
    """
    # Set the form widget to PasswordInput
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', ]


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=40)
    password = forms.CharField(widget=forms.PasswordInput)


class DriverRegisterForm(forms.ModelForm):
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)
    vehicle_type = forms.CharField(label='Vehicle type', required=True)
    license_number = forms.CharField(label='License number', required=True)
    n_passengers = forms.IntegerField(label='Number of passengers', required=True)
    special_info = forms.CharField(label='Special info', required=False)

    class Meta:
        model = VehicleInfo
        fields = ['first_name', 'last_name', 'vehicle_type', 'license_number', 'n_passengers', 'special_info', ]

    def __init__(self, *args, **kwargs):
        """
        If edit=False, then set all fields disabled = True.
        if kwargs[edit] = True, then all the fields are editable.
        """
        value = extract_edit_entry(kwargs, 'edit')
        super(DriverRegisterForm, self).__init__(*args, **kwargs)
        if value is None or value:
            return
        if not value:
            # Make all the attributes of the form to readonly.
            self.fields['first_name'].disabled = True
            self.fields['last_name'].disabled = True
            self.fields['vehicle_type'].disabled = True
            self.fields['license_number'].disabled = True
            self.fields['n_passengers'].disabled = True
            self.fields['special_info'].disabled = True


class RideRequestForm(forms.ModelForm):
    destination_addr = forms.CharField(label='Destination Address', required=True)
    arrival_time = forms.DateTimeField(label='Arrival time (Eg:2021-10-25 14:30:59)', required=True, )
    passengers = forms.IntegerField(label='Number of passengers', required=True)
    """
    Reference on why set the required attribute of the boolean field to false,
    see the note on: https://docs.djangoproject.com/en/3.1/ref/forms/fields/#Booleanfield
    """
    can_be_shared = forms.BooleanField(label='The request can be viewed by other people?', required=False, )

    class Meta:
        model = Ride
        fields = ['destination_addr', 'arrival_time', 'passengers', 'can_be_shared', 'vehicle_type',
                  'special_request', ]

    def clean_arrival_time(self):
        data = self.cleaned_data['arrival_time']
        if data >= timezone.now():
            # We only accept arrival time that is in future.
            return data
        else:
            raise ValidationError("The arrival time must be in the future!")

    def __init__(self, *args, **kwargs):
        """
        If edit=False, then set all fields disabled = True.
        if kwargs[edit] = True, then all the fields can be edited.
        """
        value = extract_edit_entry(kwargs, 'edit')
        super(RideRequestForm, self).__init__(*args, **kwargs)
        if value is None or value:
            return
        if not value:
            # Make all the attributes of the form to readonly.
            self.fields['destination_addr'].disabled = True
            self.fields['arrival_time'].disabled = True
            self.fields['passengers'].disabled = True
            self.fields['can_be_shared'].disabled = True
            self.fields['vehicle_type'].disabled = True
            self.fields['special_request'].disabled = True


class DriverFindForm(forms.Form):
    """
    This form is used for driver to find ride fulfilled his requirement.
    Can be searched by:
    1. The destination address.
    2. The arrival window.
    """
    destination_addr = forms.CharField(label='Destination', required=True)
    arrival_time_early = forms.DateTimeField(label='Acceptable arrival time.(Eg:2021-10-25 14:30:59) From:',
                                             required=True)
    arrival_time_late = forms.DateTimeField(label='Acceptable arrival time.(Eg:2021-10-26 14:30:59) To:', required=True)


class FindRideForm(forms.Form):
    """
    This class is designed for the form, which is used in:
    Find related rides for the sharer.
    The user should specify:
    1. The destination address
    2. The arrival window.
    3. The number of passengers in the party.
    """
    destination_addr = forms.CharField(label='Destination', required=True)
    arrival_time_early = forms.DateTimeField(label='Acceptable arrival time.(Eg:2021-10-25 14:30:59) From:',
                                             required=True)
    arrival_time_late = forms.DateTimeField(label='Acceptable arrival time.(Eg:2021-10-26 14:30:59) To:', required=True)
    passengers = forms.IntegerField(label='Number of passengers', required=True, validators=[
        MaxValueValidator(50),
        MinValueValidator(1),
    ])

    def __init__(self, *args, **kwargs):
        """
        If edit=False, then set all fields disabled = True.
        if kwargs[edit] = True, then all the fields can be edited.
        """
        value = extract_edit_entry(kwargs, 'driver')
        super(FindRideForm, self).__init__(*args, **kwargs)
        if value is None or not value:
            return
        if value:
            # Make all the attributes of the form to readonly.
            self.fields['passengers'].widget = forms.HiddenInput()
            self.fields['passengers'].required = False
            self.fields['destination_addr'].required = False
            self.fields['arrival_time_early'].required = False
            self.fields['arrival_time_late'].required = False

    def clean(self):
        cleaned_data = super().clean()
        early = cleaned_data.get("arrival_time_early")
        late = cleaned_data.get("arrival_time_late")
        """
        For driver find, there are three different occasions:
        1. Specify early and late
        2. Specify early without late
        3. Specify late without early
        4. Specify nothing.
        """
        if early is None and late is None:
            return
        if early is None and late is not None:
            if late < timezone.now():
                raise ValidationError("Please specify a valid early time!")
            return
        if late is None and early is not None:
            if early < timezone.now():
                raise ValidationError("Please specify a valid early time!")
            return
        if early < timezone.now():
            raise ValidationError("Please specify a valid window early time (must later than now)")
        if late >= early:
            pass
        else:
            raise ValidationError("Please specify a valid arrival window.")
