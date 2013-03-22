from django import template

from participe.challenge.models import (Challenge, Participation,
        PARTICIPATION_STATE)


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
