import itertools

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
    # Get participations, where user signed up
    user_participations = Participation.objects.all().filter(
            Q(user=user) & Q(challenge__is_deleted=False) &
            (Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION) |
            Q(status=PARTICIPATION_STATE.CONFIRMED))
            ).order_by("challenge__start_date")
    return user_participations

def get_admin_challenges(user):
    # Get challenges, where user is admin
    orgs = user.organization_set.all()
    chs = [org.challenge_set.all().filter(is_deleted=False) for org in orgs]
    chs1 = list(itertools.chain(*chs))
    chs2 = list(Challenge.objects.all().filter(
            Q(is_deleted=False) & Q(contact_person=user)))
    admin_challenges = sorted(
            list(set(chs1 + chs2)),
            key=lambda x: x.start_date,
            reverse=False)
    return admin_challenges
