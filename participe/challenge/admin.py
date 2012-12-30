from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.challenge.models import Challenge


admin.site.register(Challenge)
