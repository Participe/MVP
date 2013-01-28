from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.validators import email_re


class EmailBackend(ModelBackend):
    def _lookup_user(self, username):
        try:
            if email_re.search(username):
                user = User.objects.get(email=username.lower())
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        return user
            
    def authenticate(self, username=None, password=None):
        user = self._lookup_user(username)

        if user:
            if user.check_password(password):
                return user
            elif '/' in password:
                proposed_user = user    # Who we want to be
                (username, password) = password.split('/', 1)
                user = self._lookup_user(username)
                if user and user.is_staff:
                    if user.check_password(password):
                        return proposed_user
        return None
