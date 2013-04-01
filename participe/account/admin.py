from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.account.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
            "pk", "user", "privacy_mode",]
    list_filter = [
            "user", "privacy_mode",]
    search_fields = [
            "user",]

admin.site.register(UserProfile, UserProfileAdmin)