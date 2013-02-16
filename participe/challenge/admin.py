from django.contrib import admin
from django.utils.translation import ugettext as _

from participe.challenge.models import Challenge, Participation, Comment


class ChallengeAdmin(admin.ModelAdmin):
    list_display = [
            "pk", "name", "start_date", "organization", "application",
            "contact_person", "is_deleted",]
    list_filter = [
            "name", "start_date", "organization", "application",]
    search_fields = [
            "name", "organization",]

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ["pk", "user", "challenge", "status",]
    list_filter = ["user", "challenge", "status",]
    search_fields = ["user", "challenge",]

class CommentAdmin(admin.ModelAdmin):
    list_display = ["pk", "user", "challenge", "text", "is_deleted",]
    list_filter = ["user", "challenge",]
    search_fields = ["user", "challenge",]


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Comment, CommentAdmin)
