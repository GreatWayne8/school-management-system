from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'priority', 'timestamp', 'read')
    list_filter = ('read', 'priority', 'timestamp')
    search_fields = ('subject', 'sender__username', 'recipient__username')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    # Optional: Mark messages as read in bulk from the admin panel
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
        self.message_user(request, "Selected messages have been marked as read.")
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
        self.message_user(request, "Selected messages have been marked as unread.")
    mark_as_unread.short_description = 'Mark selected messages as unread'

# Register the Message model with the customized admin interface
admin.site.register(Message, MessageAdmin)
