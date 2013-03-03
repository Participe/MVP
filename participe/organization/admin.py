from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.organization.models import Organization


class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
            "pk", "name", "contact_person", "is_deleted",]
    list_filter = [
            "name", "contact_person", "is_deleted",]
    search_fields = [
            "name",]

admin.site.register(Organization, OrganizationAdmin)
