from django.contrib import admin
from .models import ClockInOut

class ClockInOutAdmin(admin.ModelAdmin):
    list_display = ('user', 'clock_in_time', 'clock_out_time', 'date')
    list_filter = ('date',)
    search_fields = ('user__username',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.register(ClockInOut, ClockInOutAdmin)
