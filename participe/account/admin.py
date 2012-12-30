from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.account.models import UserProfile


admin.site.register(UserProfile)
