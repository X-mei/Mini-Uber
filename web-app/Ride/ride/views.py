from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.db.models import Q
from mysite.settings import EMAIL_FROM


# Create your views here.
def index(request):
    """
    If user has already logged in, then redirect the user to the dashboard.
    Otherwise, provide the form for user to login.
    """
    # This should display a login form.
    if request.method == 'GET':
        # Verify this later.
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('ride:dashboard'))
        form = LoginForm()
        return render(request, 'ride/index.html', {'form': form, })
    else:
        # The post method.
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('ride:dashboard'))
        else:
            # We choose to display a one time error message.
            messages.error(request, 'Invalid login username or password.')
            print("Invalid login details.")
            return redirect('index')


def about(request):
    return HttpResponse("This is the about page reserverd.")


def check_if_driver(user):
    if not user.is_authenticated:
        return False
    if user.is_driver:
        return True
    return False


def register(request):
    """
    A view to provide the form for user to register.
    """
    register_state = False
    if request.method == 'POST':
        # Get the form.
        u_form = UserForm(data=request.POST)
        if u_form.is_valid():
            # We should save it as a user object.
            user = u_form.save()
            # Set its password.
            user.set_password(user.password)
            user.save()
            register_state = True
            # We should test the user whether the register is success or not.
        else:
            # There are errors inside the fields.
            print(u_form.errors)

    else:
        # Display the form for register.
        u_form = UserForm()

    return render(request, 'ride/register.html', {'u_form': u_form, 'success': register_state})


@login_required
def show_dashboard(request):
    """
    Show the dashboard of the website.
    """
    return render(request, 'ride/dashboard.html', )


@user_passes_test(check_if_driver)
def edit_driver_profile(request):
    """
    The user is validated to be a driver and logged in.
    For get method:
    Display a form with pre-populated values.
    For post method:
    Store the value into the database.
    """
    # Get the driver profile of the user.
    user = request.user
    vehicle_info = user.driver_license
    if request.method == 'GET':
        form = DriverRegisterForm(instance=vehicle_info)
    else:
        # Post method.
        form = DriverRegisterForm(request.POST, instance=vehicle_info)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, 'Invalid arguments supplied.')
    return render(request, 'ride/edit_driver.html', {
        'form': form,
    })


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def register_as_driver(request):
    """
    The page allows a user who has not registered as the driver to be registered as drivers.
    """
    user = request.user
    registered = user.is_driver
    success = False
    if request.method == 'GET':
        # Generate the form and display it.
        driver_form = DriverRegisterForm()
    else:
        # Check if the form is valid. If valid, redirect to the dashboard.
        driver_form = DriverRegisterForm(data=request.POST)
        if driver_form.is_valid():
            # We should save it as it is valid.
            veh_info = driver_form.save()
            user.driver_license = veh_info
            user.is_driver = True
            user.save()
            success = True
            # Should redirect the user to a page so that the user knows that he registered successfully.
        else:
            print(driver_form.errors)
    return render(request, 'ride/register_driver.html',
                  {'registered': registered, 'driver_form': driver_form, 'success': success})


@login_required
def request_ride(request):
    """
    This page allows a user to create new requests.
    """
    user = request.user
    if request.method == 'GET':
        # Show the form.
        request_form = RideRequestForm()
    else:
        request_form = RideRequestForm(data=request.POST)
        if request_form.is_valid():
            ride_request = request_form.save()
            ride_request.owner = user
            ride_request.save()
            # Redirect the user to a page to see his new published rides.
            return redirect('ride:view_rides', ride_id=ride_request.id)
        else:
            print(request_form.errors)
    return render(request, 'ride/request_ride.html', {
        'request_form': request_form,
    })


@login_required
def owned_rides(request):
    """
    Show all the rides that are owned by the user.
    """
    user = request.user
    rides = Ride.objects.owned_ride_for(request.user)
    # Display all the information within a template.
    return render(request, 'ride/show_owned_rides.html', {
        'rides': rides,
    })


def send_info_email(ride, subject, user):
    message = "The ride request information:\n" + ride.get_message() + "\n\n" + "Driver information:\n" + user.driver_license.get_message()
    receivers = [ride.owner.email]
    for u in ride.sharer.all():
        receivers.append(u.email)
    from_email = EMAIL_FROM
    send_mail(subject, message, from_email, receivers)


@user_passes_test(check_if_driver)
def finish_ride(request, ride_id):
    """
    This view function will allow a user to mark a ride as finished.
    """
    ride = get_object_or_404(Ride, id=ride_id)
    user = request.user
    if ride.driver != user:
        return render(request, 'ride/finish_ride.html', {
            'failed': True,
            'reason': "You are not the driver for this ride",
        })
    if ride.ride_status != 'CF':
        return render(request, 'ride/finish_ride.html', {
            'failed': True,
        })
    # The driver now is valid to mark it as finished.
    subject = "Notification: Your order has been marked as completed."
    send_info_email(ride, subject, user)
    ride.ride_status = Ride.RideStatus.COMPLETED
    ride.save()
    return redirect('ride:driver_rides')


@user_passes_test(check_if_driver)
def driver_page(request):
    user = request.user
    driver_rides = user.driver_rides.all().order_by('ride_status')
    return render(request, 'ride/show_driver_rides.html', {
        'rides': driver_rides,
    })


@login_required
def shared_rides(request):
    """
    Show all the rides that the user participate as a sharer.
    """
    user = request.user
    sharer_rides = user.shared_rides.all().filter(ride_status='OP') | user.shared_rides.all().filter(ride_status='CF')
    # Display it using a template.
    return render(request, 'ride/show_shared_rides.html', {
        'rides': sharer_rides,
    })


@login_required
def join_ride(request, ride_id, passenger_num):
    """
    Join the current user to the ride.
    Need to check whether the user can join the ride.
    """
    user = request.user
    ride = get_object_or_404(Ride, id=ride_id)
    # Check whether can join this ride.
    # Check whether the passenger_num is valid or not.
    if passenger_num <= 0 or passenger_num >= 50:
        # User cannot join the ride due to the reason:
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            'reason': "Please specify a valid passenger number!"
        })
    if ride.owner == user:
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            'reason': "You cannot join rides owned by yourself!"
        })
    if ride.ride_status != 'OP':
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            # Show the default reason.
        })
    if ride.arrival_time < timezone.now():
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            # Show the default reason.
        })
    if passenger_num + ride.passengers > 50:
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            'reason': "Too many passengers",
        })
    if not ride.can_be_shared:
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            # Show the default reason.
        })
    if user in ride.sharer.all():
        return render(request, 'ride/join_ride.html', {
            'failed': True,
            'reason': "You have already in this ride."
        })
    # The user is now valid to join the ride.
    ride.sharer.add(user)
    ride.passengers += passenger_num
    ride.save()
    return redirect('ride:shared_rides')


@login_required
def view_rides(request, ride_id):
    """
    This page is used to display all the information of a ride.
    Show the basic information about the ride request.
    If the ride can be edited by the user, then show a form for the user
    to edit.
    Otherwise, show a disabled form so that the user cannot commit.
    If the rides have drivers, also show the driver information.
    """
    ride = get_object_or_404(Ride, id=ride_id)
    # We should do some valid check to see if the user can see this page or not.
    user = request.user
    if user != ride.owner and user not in ride.sharer.all():
        if ride.driver is None:
            raise Http404("You do not have the access to this page.")
        elif ride.driver == user:
            pass
    # User have access to this page, display the information of the page.
    # Whether the user can edit this form?
    can_edit = False
    if ride.owner == user and ride.ride_status == 'OP':
        can_edit = True
    have_driver = False
    if ride.driver is not None:
        have_driver = True
    if have_driver:
        driver_info = DriverRegisterForm(instance=ride.driver.driver_license, edit=False)
    else:
        driver_info = None
    if request.method == 'GET':
        if can_edit:
            # The user can edit the page, provide a editable page.
            form = RideRequestForm(instance=ride)
        else:
            form = RideRequestForm(edit=False, instance=ride)
    else:
        if not can_edit:
            raise Http404("You do not have the access to this page.")
        form = RideRequestForm(request.POST, instance=ride)
        if form.is_valid():
            ride = form.save()
        else:
            print(form.errors)
    return render(request, 'ride/view_rides.html', {
        'ride': ride,
        'can_edit': can_edit,
        'form': form,
        'have_driver': have_driver,
        'driver_info': driver_info,
    })


@login_required
def edit_rides(request, ride_id):
    return HttpResponse("Edit rides, implement later.")


@user_passes_test(check_if_driver)
def take_ride(request, ride_id):
    """
    Allow the driver to take a ride request.
    """
    user = request.user
    ride = get_object_or_404(Ride, id=ride_id)
    if user.driver_license.n_passengers < ride.passengers:
        return render(request, 'ride/take_request.html', {
            'failed': True,
            'reason': "Not enough seats in your car!",
        })
    if ride.arrival_time < timezone.now():
        return render(request, 'ride/take_request.html', {
            'failed': True,
            'reason': "Invalid ride",
        })
    if ride.ride_status != 'OP':
        return render(request, 'ride/take_request.html', {
            'failed': True,
        })
    if user == ride.owner or user in ride.sharer.all():
        return render(request, 'ride/take_request.html', {
            'failed': True,
            'reason': "You cannot join your own ride.",
        })
    if ride.vehicle_type == '':
        pass
    else:
        if user.driver_license.vehicle_type != ride.vehicle_type:
            return render(request, 'ride/take_request.html', {
                'failed': True,
                'reason': "Vehicle info not matched!"
            })
    if ride.special_request == '':
        pass
    else:
        if user.driver_license.special_info != ride.special_request:
            return render(request, 'ride/take_request.html', {
                'failed': True,
                'reason': "Special request not matched!"
            })
    # User is valid to take this request.
    ride.ride_status = Ride.RideStatus.CONFIRMED
    ride.driver = user
    ride.save()
    # Send mails to all the users.
    subject = "Notification: Your order has been accepted by a driver"
    send_info_email(ride, subject, user)
    # Redirect the user to the driver page to see all the rides accepted by him.
    return redirect('ride:driver_rides')


@user_passes_test(check_if_driver)
def search_rides_as_driver(request):
    """
    This page find all suitable request posted by user.
    The ride can be taken by the driver.
    It will change the ride status and driver to the corresponding value.
    Send a confirmation email to all passenger.
    Can be accessed by the left column.
    """
    user = request.user
    if request.method == "GET":
        # Show the find form.
        find_form = FindRideForm(driver=True)
    else:
        # Based on the data acquired from find_form to find all the ride requests fulfilled.
        find_form = FindRideForm(driver=True, data=request.POST)
        if find_form.is_valid():
            # By default, show all the possible rides.
            suitable_rides = Ride.objects.filter(
                passengers__lte=user.driver_license.n_passengers,
                ride_status='OP',
            )
            if find_form.cleaned_data.get('arrival_time_early') is not None:
                suitable_rides = suitable_rides.filter(
                    arrival_time__gte=find_form.cleaned_data.get('arrival_time_early')
                )
            else:
                suitable_rides = suitable_rides.filter(
                    arrival_time__gte=timezone.now()
                )
            if find_form.cleaned_data.get('arrival_time_late') is not None:
                suitable_rides = suitable_rides.filter(
                    arrival_time__lte=find_form.cleaned_data.get('arrival_time_late')
                )
            if find_form.cleaned_data.get('destination_addr') == '':
                pass
            else:
                suitable_rides = suitable_rides.filter(
                    destination_addr=find_form.cleaned_data.get('destination_addr')
                )
            # If the ride specify special info, it should match.
            """
            Filter on the following terms:
            special request can be null.
            If not null, it must match up with driver's special request.
            """
            suitable_rides = suitable_rides.filter(
                Q(special_request__exact='') | Q(special_request=user.driver_license.special_info),
            )
            suitable_rides = suitable_rides.filter(
                Q(vehicle_type__exact='') | Q(vehicle_type=user.driver_license.vehicle_type),
            )
            suitable_rides = suitable_rides.exclude(
                owner=user,
            )
            suitable_rides = suitable_rides.exclude(
                sharer=user,
            )
            return render(request, 'ride/show_found_rides_driver.html', {
                'find_form': find_form,
                'displayed': True,
                'rides': suitable_rides,
            })
    print(find_form.errors)
    return render(request, 'ride/show_found_rides_driver.html', {
        'find_form': find_form,
        'displayed': False,
    })


@login_required
def search_rides_as_sharer(request):
    """
    This page find all rides that suit the sharer's need.
    Show a list of rides which will be displayed on the front page.
    """
    user = request.user
    if request.method == 'GET':
        find_form = FindRideForm()
    else:
        find_form = FindRideForm(data=request.POST)
        if find_form.is_valid():
            # User should not see rides created by themselves.
            suitable_rides = Ride.objects.filter(
                destination_addr=find_form.cleaned_data.get('destination_addr'),
                arrival_time__range=
                (find_form.cleaned_data.get('arrival_time_early'), find_form.cleaned_data.get('arrival_time_late')),
                ride_status='OP',
                can_be_shared=True,
            ).exclude(owner_id=user.id)
            return render(request, 'ride/show_found_rides.html', {
                'rides': suitable_rides,
                'find_form': find_form,
                'displayed': True,
                'passengers': find_form.cleaned_data.get('passengers'),
            })
        else:
            print(find_form.errors)
    return render(request, 'ride/show_found_rides.html', {
        'find_form': find_form,
        'displayed': False,
    })
