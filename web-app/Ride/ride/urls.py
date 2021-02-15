from django.urls import path
from . import views

app_name = 'ride'


urlpatterns = [
    path('dashboard/', views.show_dashboard, name="dashboard"),
    path('register/driver/', views.register_as_driver, name="driver_register"),
    path('driver/edit/', views.edit_driver_profile, name="edit_driver_profile"),
    path('owned/', views.owned_rides, name="owned_rides"),
    path('drived/', views.driver_page, name="driver_rides"),
    path('shared/', views.shared_rides, name="shared_rides"),
    path('join-ride/<int:ride_id>/<int:passenger_num>', views.join_ride, name="join_ride"),
    path('request-ride/', views.request_ride, name="request_ride"),
    path('view-ride/<int:ride_id>/', views.view_rides, name="view_rides"),
    path('edit-ride/<int:ride_id>/', views.edit_rides, name="edit_rides"),
    path('search-ride/driver/', views.search_rides_as_driver, name="search_rides_driver"),
    path('search-ride/sharer/', views.search_rides_as_sharer, name="search_rides_sharer"),
    path('take-request/<int:ride_id>', views.take_ride, name="take_ride"),
    path('finish-ride/<int:ride_id>', views.finish_ride, name="finish_ride"),
]
