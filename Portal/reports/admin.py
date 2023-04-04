from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import *


class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = "employee"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register Models
admin.site.register(IAACR)
admin.site.register(FacilityDropdown)
admin.site.register(NavigationHeaders)
admin.site.register(QueryReports)


# CHnage admin Panel
admin.site.site_header = "Report Portal Admin Panel"
admin.site.site_title = "RDBMS RP Admin Panel"
admin.site.index_title = "Report Portal Administration"
