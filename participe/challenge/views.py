from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from templated_email import send_templated_mail

from forms import (CreateChallengeForm, SignupChallengeForm, EditChallengeForm,
        WithdrawSignupForm)
from models import (Challenge, Participation, Comment, CHALLENGE_MODE,
        PARTICIPATION_STATE)
from participe.account.utils import is_challenge_admin
from participe.core.decorators import challenge_admin
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
    challenges = Challenge.objects.all().filter(is_deleted=False)
    return render_to_response('challenge_list.html',
            RequestContext(request, {
                'challenges': challenges,
                'CHALLENGE_MODE': CHALLENGE_MODE,
                }))

def challenge_detail(request, challenge_id):
    ctx = {}

    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    ctx.update({"challenge": challenge})

    if challenge.is_deleted:
        return render_to_response('challenge_deleted_info.html', 
                RequestContext(request, {
                        "challenge": challenge,
                        }))    

    # Only authenticated users may signup to challenge
    if request.user.is_authenticated():
        try:
            participation = Participation.objects.all().get(
                    Q(user=request.user) & Q(challenge=challenge))
            ctx.update({"participation": participation})

            if (participation.status==PARTICIPATION_STATE.CONFIRMED or
                    participation.status==
                            PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION):
                wform = WithdrawSignupForm(
                        request.POST or None, request.FILES or None,
                        instance=participation)
                ctx.update({"wform": wform})

            if participation.status==PARTICIPATION_STATE.CANCELLED_BY_USER:
                sform = SignupChallengeForm(
                        request.user, challenge, 
                        request.POST or None, request.FILES or None,
                        instance=participation)
                ctx.update({"sform": sform})
        except:
            sform = SignupChallengeForm(
                    request.user, challenge, 
                    request.POST or None, request.FILES or None)
            ctx.update({"sform": sform})

        # Weird block, but it's the only way to describe the logic with
        # processing of states with forms, such (None, sform, wform)
        if request.method == "POST":
            # User signs up to challenge
            try:
                if sform.is_valid():
                    sform.save()
                    if challenge.application==CHALLENGE_MODE.FREE_FOR_ALL:
                        send_templated_mail(
                            template_name="challenge_successful_signup",
                            from_email="from@example.com", 
                            recipient_list=[user.email,], 
                            context={
                                    "user": user,
                                    "challenge": challenge,
                                    },)
            except NameError:
                pass

            # User withdraws his application
            try:
                if wform.is_valid:
                    wform.save()
            except NameError:
                pass
            return redirect("challenge_detail", challenge.pk)
        ctx.update({"is_admin": is_challenge_admin(user, challenge)})

    # Extract participations
    waited = Participation.objects.all().filter(
            Q(challenge=challenge) & 
            Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION)
            )
    ctx.update({"waited": waited})

    confirmed = Participation.objects.all().filter(
            Q(challenge=challenge) & Q(status=PARTICIPATION_STATE.CONFIRMED)
            )
    ctx.update({"confirmed": confirmed})

    # Extract comments
    comments = Comment.objects.all().filter(
            Q(challenge=challenge) & Q(is_deleted=False)
            ).order_by("created_at")
    ctx.update({"comments": comments})

    ctx.update({"PARTICIPATION_STATE": PARTICIPATION_STATE})
    ctx.update({"CHALLENGE_MODE": CHALLENGE_MODE})

    return render_to_response('challenge_detail.html',
            RequestContext(request, ctx))

@login_required
@challenge_admin
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def challenge_edit(request, challenge_id):
    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    form = EditChallengeForm(
            user, request.POST or None, request.FILES or None,
            instance=challenge)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            participations = Participation.objects.all().filter(
                    Q(challenge=challenge) &
                    (Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION) |
                            Q(status=PARTICIPATION_STATE.CONFIRMED))
                    )
            waited = Participation.objects.all().filter(
                    Q(challenge=challenge) &
                    Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION)
                    )
            if "delete" in request.POST:
                challenge.is_deleted = True
                challenge.save()
                
                for participation in participations:
                    send_templated_mail(
                            template_name="challenge_deleted",
                            from_email="from@example.com", 
                            recipient_list=[participation.user.email,], 
                            context={
                                    "user": participation.user,
                                    "challenge": participation.challenge,
                                    },)
            #is_date_time_changed:
            elif ("start_date" in form.changed_data or
                    "start_time" in form.changed_data):
                for participation in participations:
                    send_templated_mail(
                            template_name="challenge_changed",
                            from_email="from@example.com", 
                            recipient_list=[participation.user.email,], 
                            context={
                                    "user": participation.user,
                                    "challenge": participation.challenge,
                                    },)
            #is_application_changed:
            if ("application" in form.changed_data and
                    challenge.application==CHALLENGE_MODE.FREE_FOR_ALL):
                for participation in waited:
                    participation.status = PARTICIPATION_STATE.CONFIRMED
                    participation.date_accepted = datetime.now()
                    participation.save()

                    send_templated_mail(
                            template_name="challenge_application_changed",
                            from_email="from@example.com", 
                            recipient_list=[participation.user.email,], 
                            context={
                                    "user": participation.user,
                                    "challenge": participation.challenge,
                                    },)
            return redirect("challenge_detail", challenge_id)
    return render_to_response('challenge_edit.html', 
            RequestContext(request, {'form': form}))

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
            recipient_list=[participation.user.email,], 
            context={
                    "user": participation.user,
                    "challenge": participation.challenge,
                    },)
    return redirect("challenge_detail", participation.challenge.pk)

@login_required
@challenge_admin
def participation_remove(request, challenge_id):
    if request.method == "POST":
        participation_id = request.POST["participation_id"]
        value = request.POST["value"]
        cancellation_text = request.POST["text"]
        
        participation = get_object_or_404(Participation, pk=participation_id)

        if value=="Remove":
            participation.status = PARTICIPATION_STATE.CANCELLED_BY_USER
            template_name = "challenge_participation_removed"
        elif value=="Reject":
            participation.status = PARTICIPATION_STATE.CONFIRMATION_DENIED
            template_name = "challenge_participation_rejected"
        
        participation.cancellation_text = cancellation_text
        participation.date_cancelled = datetime.now()

        participation.save()

        send_templated_mail(
                template_name=template_name,
                from_email="from@example.com", 
                recipient_list=[participation.user.email,], 
                context={
                        "user": participation.user,
                        "challenge": participation.challenge,
                        "participation": participation,
                        },)
        return redirect("challenge_detail", participation.challenge.pk)
    return redirect("challenge_list")

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
        return redirect("challenge_detail", request.POST["challenge_id"])
    return redirect("challenge_list")

@login_required
@challenge_admin
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_deleted = True
    comment.save()
    return redirect("challenge_detail", comment.challenge.pk)
