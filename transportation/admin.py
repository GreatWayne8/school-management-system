from django.contrib import admin
from .models import Route, Bus, StudentPickup, TransportRequest

# Customizing the Route Admin
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_name', 'start_location', 'end_location')
    search_fields = ('route_name', 'start_location', 'end_location')
    list_filter = ('start_location', 'end_location')

# Customizing the Bus Admin
@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'route', 'driver', 'capacity')
    search_fields = ('bus_number', 'driver__username')
    list_filter = ('route', 'driver')
    filter_horizontal = ('teachers',)  # For ManyToManyField

# Customizing the StudentPickup Admin
@admin.register(StudentPickup)
class StudentPickupAdmin(admin.ModelAdmin):
    list_display = ('student', 'pickup_location', 'dropoff_location', 'route', 'bus')
    search_fields = ('student__user__username', 'route__route_name', 'bus__bus_number')
    list_filter = ('route', 'bus')

# Customizing the TransportRequest Admin
@admin.register(TransportRequest)
class TransportRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'transport_type', 'status', 'pickup_time', 'dropoff_time')
    search_fields = ('student__user__username', 'pickup_location', 'dropoff_location')
    list_filter = ('status', 'transport_type')

