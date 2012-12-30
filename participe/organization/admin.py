from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.organization.models import Organization


admin.site.register(Organization)
