import datetime

from django import template
from django.db.models import Sum, Q

from participe.account.utils import get_user_participations, get_admin_challenges
from participe.challenge.models import (Challenge, Participation,
        CHALLENGE_STATUS, PARTICIPATION_STATE)


register = template.Library()

@register.assignment_tag
def need_to_know_tag(request, account):
    user = request.user

    if Challenge.objects.filter(contact_person=account, is_deleted=False):
        return True

    if user.is_authenticated():
        chs = Challenge.objects.filter(
            pk__in=Participation.objects.filter(
                user=account,
                challenge__is_deleted=False,
                status__in=[
                    PARTICIPATION_STATE.CONFIRMED,
                    PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
                    PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT,
                    PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION,]
                ).values_list("challenge_id", flat=True),
            contact_person=user
            )
        if chs:
            return True
    return False

@register.assignment_tag
def sum_of_hours_spent_tag(account):
    sum_of_hours_spent = Challenge.objects.filter(
        pk__in=Participation.objects.filter(
            user=account,
            challenge__is_deleted=False,
            status=PARTICIPATION_STATE.ACKNOWLEDGED
        ).values_list("challenge_id", flat=True)).aggregate(Sum("duration"))
    return sum_of_hours_spent["duration__sum"]

@register.assignment_tag
def as_user_action_required_count(request):
    return get_user_participations(request.user).filter(
            status=PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION
            ).count()

@register.assignment_tag
def as_admin_action_required_count(request):
    return get_admin_challenges(request.user).filter(
            Q(pk__in=Participation.objects.filter(
                    status__in=[
                            PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
                            PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
                            ]).values_list("challenge_id", flat=True)
            ) | Q(
                    start_date__lt=datetime.date.today(),
                    status=CHALLENGE_STATUS.UPCOMING
                    )
            ).count()