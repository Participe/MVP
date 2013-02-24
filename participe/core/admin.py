from django.contrib import admin
from django.contrib.auth.models import Group
from auth_remember.models import RememberToken
from social_auth.models import Association, Nonce, UserSocialAuth

class EmptyModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}

admin.site.unregister(Group)

admin.site.unregister(RememberToken)
admin.site.register(RememberToken, EmptyModelAdmin)

admin.site.unregister(Association)
admin.site.register(Association, EmptyModelAdmin)
    
admin.site.unregister(Nonce)
admin.site.register(Nonce, EmptyModelAdmin)

admin.site.unregister(UserSocialAuth)
admin.site.register(UserSocialAuth, EmptyModelAdmin)
