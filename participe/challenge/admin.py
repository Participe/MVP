from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.challenge.models import Challenge, Participation, Comment


admin.site.register(Challenge)
admin.site.register(Participation)
admin.site.register(Comment)
