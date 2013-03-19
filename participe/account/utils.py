from django.db.models import Q

from participe.challenge.models import (Participation, Challenge,
        PARTICIPATION_STATE)

#TODO Expand django.contrib.auth.models.User and move methods there

def is_challenge_admin(user, challenge):
    admin_challenges = get_admin_challenges(user)
    if challenge in admin_challenges:
        return True
    else:
        return False

def get_user_participations(user):
    # Get all user participations
    user_participations = Participation.objects.filter(
            user=user,
            challenge__is_deleted=False
            )
    return user_participations

def get_admin_challenges(user):
    # Get challenges, where user is admin
    orgs = user.organization_set.all()
    admin_challenges = Challenge.objects.filter(
            Q(is_deleted=False) & 
            (Q(organization__in=orgs) | Q(contact_person=user))
            )
    return admin_challenges
