from django.shortcuts import get_object_or_404
from participe.account.models import UserProfile


def user_profile_completed(user):
    
    try:
        profile = get_object_or_404(UserProfile, user=user)
        return profile.is_completed
    except:
        return False
