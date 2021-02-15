from django.test import TestCase, Client
from .models import *
from .forms import *
from .views import *
# Create your tests here.


class VehicleInfoTests(TestCase):
    
    def test_invalid_passengers_form(self):
        """
        Test different situations for DriverRegisterForm
        """
        form_data = {
            'first_name':"fake",
            'last_name':"fake",
            'vehicle_type':"fake",
            'license_number':"fake",
            'n_passengers':5
        }
        # What if the user just specify nothing in the name field.
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), True)

        form_data['n_passengers'] = -1
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), False)

        form_data['n_passengers'] = 0
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), False)

        form_data['n_passengers'] = 1
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), True)

        form_data['n_passengers'] = 50
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), True)

        form_data['n_passengers'] = 51
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), False)

        form_data['n_passengers'] = 5
        # Should not allow empty string.
        form_data['first_name'] = ""
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), False)
                
        form_data['n_passengers'] = 5
        # Should not allow empty string.
        form_data['first_name'] = "asdf"
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), True)

        form_data['n_passengers'] = 5
        # Should not allow empty string.
        form_data['first_name'] = "    "
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), False)
        
        form_data['special_info'] = "wow"
        form_data['first_name'] = "fake"
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), True)

        
        form_data['special_info'] = ''
        form_data['first_name'] = "fake"
        dr = DriverRegisterForm(data=form_data)
        self.assertIs(dr.is_valid(), True)



class UserCreateTest(TestCase):
    def test_user_create(self):
        """
        Tests for user create form.
        """
        form_data = {
            'username': 'test',
            'password':123456
        }
        # Test for no email input
        u_form = UserForm(data=form_data)
        self.assertIs(u_form.is_valid(), False)

        form_data['email'] = 'test@example.com'
        u_form = UserForm(data=form_data)
        self.assertIs(u_form.is_valid(), True)

        form_data['email'] = ''
        u_form = UserForm(data=form_data)
        self.assertIs(u_form.is_valid(), False)

        form_data['email'] = 'test@example.com'
        form_data['username'] = ''
        u_form = UserForm(data=form_data)
        self.assertIs(u_form.is_valid(), False)

        # Test unique attributes on username and email.
        form_data['email'] = 'test@example.com'
        form_data['username'] = 'test1'
        u_form = UserForm(data=form_data)
        self.assertIs(u_form.is_valid(), True)

        u_form.save()

        # Existing user with the same email.
        form_data['username'] = 'test2'
        u_form = UserForm(data=form_data)
        self.assertRaises(ValueError, u_form.save)

        # This should success with a different email.
        form_data['email'] = 'test2@example.com'
        u_form = UserForm(data=form_data)
        u_form.save()

        form_data['email']= 'test3@example.com'
        u_form = UserForm(data=form_data)
        self.assertRaises(ValueError, u_form.save)
