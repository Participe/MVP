from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User

from celery.task import task, periodic_task
from templated_email import send_templated_mail

from models import Challenge, Participation, PARTICIPATION_STATE


@periodic_task(run_every=timedelta(hours=24))
def remind_accept_reject_application():
    # Select users, who have created Challenge(s)
    users = User.objects.filter(
            is_active=True,
            pk__in=Challenge.objects.filter(
                    is_deleted=False
                    ).values_list("contact_person__pk", flat=True))

    for user in users:
        # Select challenges, created by User
        challenges = Challenge.objects.filter(
                pk__in=Participation.objects.filter(
                        user=user, 
                        challenge__is_deleted=False, 
                        status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
                        ).values_list("challenge_id", flat=True))
        if challenges:
            content = ""
            for challenge in challenges:
                participations = Participation.objects.filter(
                        user=user,
                        challenge=challenge,
                        status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION                    
                )
                content += ("<p>There are {0} of people,"
                        " waiting for approval on challenge"
                        " <a href='http://{1}{2}'>{3}</a></p><br/>".format(
                        participations.count(), settings.DOMAIN_NAME, 
                        challenge.get_absolute_url(), challenge.name))
                send_templated_mail(
                    template_name="remind_accept_reject_application",
                    from_email="from@example.com", 
                    recipient_list=[user.email,], 
                    context={
                            "user": user,
                            "content": content,
                            },)
