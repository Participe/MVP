from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User

from celery.schedules import crontab
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
                        status__in=[
                                PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
                                PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
                                ]
                        ).values_list("challenge_id", flat=True))
        if challenges:
            content = ""
            for challenge in challenges:
                # Looking for people, waiting for confirmation
                participations = Participation.objects.filter(
                        user=user,
                        challenge=challenge,
                        status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
                        )
                if participations:
                    content += ("<p>There are {0} of people,"
                            " waiting for approval on challenge"
                            " <a href='http://{1}{2}'>{3}</a></p><br/>".format(
                            participations.count(), settings.DOMAIN_NAME,
                            challenge.get_absolute_url(), challenge.name))

                # Looking for people, waiting for acknowledgement
                participations = Participation.objects.filter(
                        user=user,
                        challenge=challenge,
                        status=PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
                        )
                if participations:
                    content += ("<p>There are {0} of people, waiting for"
                            " acknowledgment of their selfreflection on"
                            " challenge"
                            " <a href='http://{1}{2}'>{3}</a></p><br/>".format(
                            participations.count(), settings.DOMAIN_NAME,
                            challenge.get_absolute_url(), challenge.name))

                # Send e-mail
                send_templated_mail(
                        template_name="remind_accept_reject_application",
                        from_email="from@example.com",
                        recipient_list=[user.email,],
                        context={
                                "user": user,
                                "content": content,
                                },)

@periodic_task(run_every=crontab(hour=19, minute=0))
def remind_challenge_participation():
    participations = Participation.objects.filter(
            challenge__is_deleted=False,
            status=PARTICIPATION_STATE.CONFIRMED
            )
    for participation in participations:
        user = participation.user
        challenge = participation.challenge
        td = challenge.start_date - date.today()
        if td.days==1:
            send_templated_mail(
                    template_name="remind_challenge_participation",
                    from_email="from@example.com",
                    recipient_list=[user.email,],
                    context={
                            "user": user,
                            "challenge": challenge,
                            },)
