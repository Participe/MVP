from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from templated_email import send_templated_mail
from datetime import date, datetime
import locale

from forms import (CreateChallengeForm, SignupChallengeForm, EditChallengeForm,
                   WithdrawSignupForm, SelfreflectionForm)
from models import (Challenge, Participation, Comment, CHALLENGE_MODE,
                    CHALLENGE_STATUS, PARTICIPATION_STATE, PARTICIPATION_REMOVE_MODE)

from participe.account.models import PRIVACY_MODE
from participe.account.utils import is_challenge_admin
from participe.core.decorators import challenge_admin
from participe.core.http import Http501
from participe.core.user_tests import user_profile_completed


@login_required
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def challenge_create(request):
    form = CreateChallengeForm(
        request.user, request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("challenge_list")

    return render_to_response('challenge_create.html',
                              RequestContext(request, {'form': form}))


def challenge_list(request):
    challenges = Challenge.objects.all().filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=date.today(),
        is_deleted=False)
    return render_to_response('challenge_list.html',
                              RequestContext(request, {
                                  'challenges': challenges,
                                  'CHALLENGE_MODE': CHALLENGE_MODE,
                              }))


def challenge_detail(request, challenge_id, org_slug=None, chl_slug=None):
    ctx = {}

    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    ctx.update({"challenge": challenge})

    if challenge.is_deleted:
        return render_to_response('challenge_deleted_info.html',
                                  RequestContext(request, {
                                      "challenge": challenge,
                                      "subject": _("%(challenge_name)s was cancelled")
                                                 % {"challenge_name": challenge.name},
                                  }))

    # Only authenticated users may signup to challenge
    if request.user.is_authenticated():
        try:
            participation = Participation.objects.all().get(
                Q(user=request.user) & Q(challenge=challenge))
            ctx.update({"participation": participation})

            if (participation.status == PARTICIPATION_STATE.CONFIRMED or
                        participation.status == PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION):
                wform = WithdrawSignupForm(
                    request.POST or None, request.FILES or None,
                    instance=participation)
                ctx.update({"wform": wform})

            if participation.status == PARTICIPATION_STATE.CANCELLED_BY_USER:
                sform = SignupChallengeForm(
                    request.user, challenge,
                    request.POST or None, request.FILES or None,
                    instance=participation)
                ctx.update({"sform": sform})

            if participation.status == PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION:
                rform = SelfreflectionForm(
                    request.POST or None, request.FILES or None,
                    instance=participation)
                ctx.update({"rform": rform})

                if not participation.is_selfreflection_rejected:
                    pform = WithdrawSignupForm(
                        request.POST or None, request.FILES or None,
                        instance=participation)
                    ctx.update({"pform": pform})
        except:
            sform = SignupChallengeForm(
                request.user, challenge,
                request.POST or None, request.FILES or None)
            ctx.update({"sform": sform})

        # Weird block, but it's the only way to describe the logic with
        # processing of states with forms, such (None, sform, wform, rform)
        if request.method == "POST":
            # User signs up to challenge
            try:
                if sform.is_valid():
                    sform.save()
                    if challenge.application == CHALLENGE_MODE.FREE_FOR_ALL:
                        send_templated_mail(
                            template_name="challenge_successful_signup",
                            from_email=settings.EMAIL_SENDER,
                            recipient_list=[user.email, ],
                            context={
                                "user": user,
                                "challenge": challenge,
                                "challenge_url": challenge.get_full_url(request),
                                "subject": _("Participation Confirmation for %(challenge_name)")
                                        % {"challenge_name": challenge.name},
                            }, )
            except NameError:
                pass

            # User withdraws his application
            try:
                if wform.is_valid():
                    wform.save()
            except NameError:
                pass

            # User leaves his self-reflection
            try:
                if rform.is_valid():
                    rform.save()
            except NameError:
                pass

            # User didn't participate after all
            try:
                if pform.is_valid():
                    pform.save()
            except NameError:
                pass
            return redirect(challenge.get_absolute_url())
        ctx.update({"is_admin": is_challenge_admin(user, challenge)})

    # Extract participations
    confirmed = Participation.objects.all().filter(
        challenge=challenge,
        status__in=[
            PARTICIPATION_STATE.CONFIRMED,
            PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION,
            PARTICIPATION_STATE.ACKNOWLEDGED,
            PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
        ]
    )
    ctx.update({"confirmed": confirmed})

    waiting_for_confirmation = Participation.objects.all().filter(
        challenge=challenge,
        status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
    )
    ctx.update({"waiting_for_confirmation": waiting_for_confirmation})

    waiting_for_acknowledgement = Participation.objects.all().filter(
        challenge=challenge,
        status=PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
    )
    ctx.update({"waiting_for_acknowledgement": waiting_for_acknowledgement})

    # Extract comments
    comments = Comment.objects.all().filter(
        Q(challenge=challenge) & Q(is_deleted=False)
    ).order_by("created_at")
    ctx.update({"comments": comments})

    ctx.update({"PARTICIPATION_STATE": PARTICIPATION_STATE})
    ctx.update({"CHALLENGE_STATUS": CHALLENGE_STATUS})
    ctx.update({"CHALLENGE_MODE": CHALLENGE_MODE})
    ctx.update({"PRIVACY_MODE": PRIVACY_MODE})
    ctx.update({"PARTICIPATION_REMOVE_MODE": PARTICIPATION_REMOVE_MODE})

    return render_to_response('challenge_detail.html',
                              RequestContext(request, ctx))


@login_required
@challenge_admin
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def challenge_edit(request, challenge_id):
    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if challenge.status == CHALLENGE_STATUS.COMPLETED:
        raise Http501

    form = EditChallengeForm(
        user,
        request.POST or None,
        request.FILES or None,
        instance=challenge)

    #save button clicked
    if request.method == "POST":
        if form.is_valid():
            form.save()

            ctx = {}
            ctx.update({
                "user": user,
                "challenge": challenge,
                "challenge_url": challenge.get_full_url(request),
            })
            locale.setlocale(locale.LC_TIME, "de_CH.utf8")

            participations = Participation.objects.all().filter(
                Q(challenge=challenge) &
                (
                    Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION) |
                    Q(status=PARTICIPATION_STATE.CONFIRMED)
                )
            )

            waited = Participation.objects.all().filter(
                Q(challenge=challenge) &
                Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION)
            )

            if "delete" in request.POST:
                challenge.is_deleted = True
                challenge.save()

                ctx.update({"subject": _("%(challenge_name)s was cancelled")
                                       % {"challenge_name": challenge.name}})
                for participation in participations:
                    send_templated_mail(
                        template_name="challenge_deleted",
                        from_email=settings.EMAIL_SENDER,
                        recipient_list=[participation.user.email, ],
                        context=ctx)

            #is_date_time_changed:
            elif "start_date" in form.changed_data or "start_time" in form.changed_data:
                ctx.update({"subject": _("%(challenge)s now starts at %(start_date)s at %(start_time)s") % {
                    "challenge": challenge.name,
                    "start_date": challenge.start_date.strftime("%A, %d. %B"),
                    "start_time": challenge.start_time.strftime("%H:%M"),
                }})
                for participation in participations:
                    send_templated_mail(
                        template_name="challenge_changed",
                        from_email=settings.EMAIL_SENDER,
                        recipient_list=[participation.user.email, ],
                        context=ctx, )

            if "application" in form.changed_data and challenge.application == CHALLENGE_MODE.FREE_FOR_ALL:
                ctx.update({"subject": _("You were accepted to '%(challenge)s on Participe!") % {"challenge": challenge.name}})
                for participation in waited:
                    #if we change a challenge state from confirmation required to free-for-all,
                    #we automatically accept all people who are currently waiting for their
                    #applications to be accepted. We also inform them by email about this.
                    participation.status = PARTICIPATION_STATE.CONFIRMED
                    participation.date_accepted = datetime.now()
                    participation.save()

                    send_templated_mail(
                        template_name="challenge_application_changed",
                        from_email=settings.EMAIL_SENDER,
                        recipient_list=[participation.user.email, ],
                        context=ctx, )

            return redirect(challenge.get_absolute_url())

    return render_to_response('challenge_edit.html', RequestContext(request, {'form': form}))


@login_required
@challenge_admin
def challenge_complete(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    if request.method == "POST":
        description = request.POST["description"]
        challenge.description = description
        challenge.status = CHALLENGE_STATUS.COMPLETED
        challenge.save()

        redirect_to = (
            u"<a href='http://{0}/accounts/login?next={1}'>{2}</a>"
            u"".format(
                request.get_host(),
                challenge.get_absolute_url(),
                challenge.name))

        # CONFIRMED -->> WAITING FOR SELFREFLECTION
        participations = Participation.objects.filter(
            challenge=challenge,
            status=PARTICIPATION_STATE.CONFIRMED
        )
        for participation in participations:
            participation.status = PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION
            participation.save()

            send_templated_mail(
                template_name="challenge_participation_request_selfreflection",
                from_email="from@example.com",
                recipient_list=[participation.user.email, ],
                context={
                    "user": participation.user,
                    "challenge": challenge,
                    "challenge_url":
                        participation.challenge.get_full_url(request),
                    "redirect_to": redirect_to,
                    "subject": _("Self-reflection requested for %(challenge_name)s")
                               % {"challenge_name": participation.challenge.name},
                }, )

        # WAITING FOR CONFIRMATION -->> CANCELLED BY ADMIN
        participations = Participation.objects.filter(
            challenge=challenge,
            status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
        )
        for participation in participations:
            participation.status = PARTICIPATION_STATE.CANCELLED_BY_ADMIN
            participation.cancellation_text = "Challenge completed"
            participation.save()

            send_templated_mail(
                template_name="challenge_participation_rejected",
                from_email=settings.EMAIL_SENDER,
                recipient_list=[participation.user.email, ],
                context={
                    "user": participation.user,
                    "challenge": challenge,
                    "subject": _("You were not accepted for %(challenge_name)s")
                               % {"challenge_name": participation.challenge.name},
                    "challenge_url":
                        participation.challenge.get_full_url(request),
                    "participation": participation,
                }, )

        return redirect(challenge.get_absolute_url())
    return redirect("challenge_list")


@login_required
@challenge_admin
def participation_accept(request, participation_id):
    participation = get_object_or_404(Participation, pk=participation_id)
    participation.status = PARTICIPATION_STATE.CONFIRMED
    participation.date_accepted = datetime.now()
    participation.save()

    send_templated_mail(
        template_name="challenge_participation_accepted",
        from_email="from@example.com",
        recipient_list=[participation.user.email, ],
        context={
            "user": participation.user,
            "challenge": participation.challenge,
            "challenge_url":
                participation.challenge.get_full_url(request),
        }, )
    return redirect(participation.challenge.get_absolute_url())


@login_required
@challenge_admin
def participation_remove(request, challenge_id):
    if request.method == "POST":
        ctx = {}
        participation_id = request.POST["participation_id"]
        value = request.POST["value"]
        text = request.POST["text"]

        participation = get_object_or_404(Participation, pk=participation_id)
        ctx.update({
            "user": participation.user,
            "challenge": participation.challenge,
            "challenge_url": participation.challenge.get_full_url(request),
            "participation": participation, })

        if value == "Remove":
            participation.status = PARTICIPATION_STATE.CANCELLED_BY_ADMIN
            template_name = "challenge_participation_removed"
        elif value == "Reject":
            participation.status = PARTICIPATION_STATE.CONFIRMATION_DENIED
            template_name = "challenge_participation_rejected"
        elif value == "Reject self-reflection":
            participation.status = PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION
            template_name = "challenge_participation_selfreflection_rejected"
            redirect_to = (
                u"<a href='http://{0}/accounts/login?next={1}'>{2}</a>"
                u"".format(
                    request.get_host(),
                    participation.challenge.get_absolute_url(),
                    participation.challenge.name))
            ctx.update({"redirect_to": redirect_to})
        elif value == "Acknowledge":
            participation.status = PARTICIPATION_STATE.ACKNOWLEDGED
            template_name = "challenge_participation_acknowledged"
            redirect_to = (
                u"<a href='http://{0}/accounts/login?"
                u"next=/accounts/profile/view/'>profile</a>"
                u"".format(
                    request.get_host()
                ))
            ctx.update({
                "redirect_to": redirect_to,
                "subject": _("You were accepted for %(challenge_name)s")
                           % {"challenge_name": participation.challenge.name},
                })

        if value == "Remove" or value == "Reject":
            participation.cancellation_text = text
            participation.date_cancelled = datetime.now()
        elif value == "Reject self-reflection":
            participation.selfreflection_rejection_text = text
            participation.date_selfreflection_rejection = datetime.now()
        elif value == "Acknowledge":
            participation.acknowledgement_text = text
            participation.date_acknowledged = datetime.now()
        participation.save()

        send_templated_mail(
            template_name=template_name,
            from_email="from@example.com",
            recipient_list=[participation.user.email, ],
            context=ctx, )
        return redirect(participation.challenge.get_absolute_url())
    return redirect("challenge_list")


@csrf_exempt
@login_required
@challenge_admin
def ajax_participation_accept(request, challenge_id):
    if request.is_ajax():
        participation_id = request.POST.get("participation_id", "")
        try:
            participation = Participation.objects.get(pk=participation_id)
        except:
            return HttpResponse("An error has been encountered")

        participation.status = PARTICIPATION_STATE.CONFIRMED
        participation.date_accepted = datetime.now()
        participation.save()

        send_templated_mail(
            template_name="challenge_participation_accepted",
            from_email="from@example.com",
            recipient_list=[participation.user.email, ],
            context={
                "user": participation.user,
                "challenge": participation.challenge,
                "subject": _("You were accepted for %(challenge_name)s")
                           % {"challenge_name": participation.challenge.name},
                "challenge_url": participation.challenge.get_full_url(request),

            }, )
        return HttpResponse()
    return HttpResponse("An error has been encountered!")


@csrf_exempt
@login_required
@challenge_admin
def ajax_participation_remove(request, challenge_id):
    if request.is_ajax():
        ctx = {}
        participation_id = request.POST.get("participation_id", "")
        value = request.POST.get("action_id", "")
        text = request.POST.get("text", "")

        try:
            participation = Participation.objects.get(pk=participation_id)
        except:
            return HttpResponse("An error has been encountered")

        ctx.update({
            "user": participation.user,
            "challenge": participation.challenge,
            "participation": participation, })

        if value == PARTICIPATION_REMOVE_MODE.REMOVE_APPLICATION:
            participation.status = PARTICIPATION_STATE.CANCELLED_BY_ADMIN
            template_name = "challenge_participation_removed"
        elif value == PARTICIPATION_REMOVE_MODE.REJECT_APPLICATION:
            participation.status = PARTICIPATION_STATE.CONFIRMATION_DENIED
            template_name = "challenge_participation_rejected"

        participation.cancellation_text = text
        participation.date_cancelled = datetime.now()
        participation.save()

        send_templated_mail(
            template_name=template_name,
            from_email="from@example.com",
            recipient_list=[participation.user.email, ],
            context=ctx, )
        return HttpResponse()
    return HttpResponse("An error has been encountered!")


@csrf_exempt
@login_required
@challenge_admin
def ajax_accept_reject_selfreflection(request, challenge_id):
    if request.is_ajax():
        ctx = {}
        participation_id = request.POST.get("participation_id", "")
        value = request.POST.get("action_id", "")
        text = request.POST.get("text", "")

        try:
            participation = Participation.objects.get(pk=participation_id)
        except:
            return HttpResponse("An error has been encountered")

        ctx.update({
            "user": participation.user,
            "challenge": participation.challenge,
            "challenge_url": participation.challenge.get_full_url(request),
            "participation": participation, })

        if value == PARTICIPATION_REMOVE_MODE.REJECT_SELFREFLECTION:
            participation.status = PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION
            template_name = "challenge_participation_selfreflection_rejected"
            redirect_to = (
                u"<a href='http://{0}/accounts/login?next={1}'>{2}</a>"
                u"".format(
                    request.get_host(),
                    participation.challenge.get_absolute_url(),
                    participation.challenge.name))
            ctx.update({"redirect_to": redirect_to})
        elif value == PARTICIPATION_REMOVE_MODE.ACKNOWLEDGE:
            participation.status = PARTICIPATION_STATE.ACKNOWLEDGED
            template_name = "challenge_participation_acknowledged"
            redirect_to = (
                u"<a href='http://{0}/accounts/login?"
                u"next=/accounts/profile/view/'>profile</a>"
                u"".format(
                    request.get_host()
                ))
            ctx.update({"redirect_to": redirect_to})

        if value == PARTICIPATION_REMOVE_MODE.REJECT_SELFREFLECTION:
            participation.selfreflection_rejection_text = text
            participation.date_selfreflection_rejection = datetime.now()
        elif value == PARTICIPATION_REMOVE_MODE.ACKNOWLEDGE:
            participation.acknowledgement_text = text
            participation.date_acknowledged = datetime.now()
        participation.save()

        try:
            send_templated_mail(
                template_name=template_name,
                from_email="from@example.com",
                recipient_list=[participation.user.email, ],
                context=ctx, )
        except Exception, e:
            print ">>> %s - %s - %s" % (e, e.message, e.__class__)
        return HttpResponse()
    return HttpResponse("An error has been encountered!")


@login_required
def comment_add(request):
    if request.method == "POST":
        challenge_id = request.POST.get('challenge_id', '')
        comment_text = request.POST.get('comment', '')

        challenge = get_object_or_404(Challenge, pk=challenge_id)
        comment = Comment.objects.create(
            user=request.user,
            challenge=challenge,
            text=comment_text,
        )
        comment.save()
        return redirect(challenge.get_absolute_url())
    return redirect("challenge_list")


@login_required
@challenge_admin
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_deleted = True
    comment.save()
    return redirect(comment.challenge.get_absolute_url())
