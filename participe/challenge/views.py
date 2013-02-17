from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from templated_email import send_templated_mail

from forms import CreateChallengeForm, SignupChallengeForm, EditChallengeForm
from models import Challenge, Participation, Comment
from participe.account.utils import is_challenge_admin
from participe.core.decorators import challenge_admin
from participe.core.user_tests import user_profile_completed
from participe.challenge.models import CHALLENGE_MODE
from participe.challenge.models import PARTICIPATION_STATE

            
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
    challenges = Challenge.objects.all()
    return render_to_response('challenge_list.html',
            RequestContext(request, {'challenges': challenges}))

def challenge_detail(request, challenge_id):
    ctx = {}

    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    ctx.update({"challenge": challenge})

    # Only authenticated users may signup to challenge
    if request.user.is_authenticated():
        try:
            participation = Participation.objects.all().get(
                    Q(user=request.user) & Q(challenge=challenge))
            ctx.update({"participation": participation})
        except:
            form = SignupChallengeForm(
                    request.user, challenge, request.POST or None,
                    request.FILES or None)
            if request.method == "POST":
                if form.is_valid():
                    form.save()

                    if challenge.application == CHALLENGE_MODE.FREE_FOR_ALL:
                        send_templated_mail(
                            template_name="challenge_successful_signup",
                            from_email="from@example.com", 
                            recipient_list=[user.email,], 
                            context={
                                    "user": user,
                                    "challenge": challenge,
                                    },)
                    else:
                        # TODO Send notification to Challenge Admin?
                        pass
                    return redirect("challenge_detail", challenge.pk)
            ctx.update({"form": form})
        ctx.update({"is_admin": is_challenge_admin(user, challenge)})

    # Extract participations
    waited = Participation.objects.all().filter(
            Q(challenge=challenge) & Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION)
            )
    ctx.update({"waited": waited})

    confirmed = Participation.objects.all().filter(
            Q(challenge=challenge) & Q(status=PARTICIPATION_STATE.CONFIRMED)
            )
    ctx.update({"confirmed": confirmed})

    # Extract comments
    comments = Comment.objects.all().filter(
            Q(challenge=challenge) & Q(is_deleted=False))
    ctx.update({"comments": comments})

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
            is_date_time_changed = False
            if ("start_date" in form.changed_data or
                    "start_time" in form.changed_data):
                is_date_time_changed = True
            form.save()

            participations = Participation.objects.all().filter(
                    Q(challenge=challenge) &
                    (Q(status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION) | Q(status=PARTICIPATION_STATE.CONFIRMED))
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
            elif is_date_time_changed:
                for participation in participations:
                    send_templated_mail(
                            template_name="challenge_changed",
                            from_email="from@example.com", 
                            recipient_list=[participation.user.email,], 
                            context={
                                    "user": participation.user,
                                    "challenge": participation.challenge,
                                    },)
            return redirect("challenge_list")

    return render_to_response('challenge_edit.html', 
            RequestContext(request, {'form': form}))

@login_required
def participation_accept(request, participation_id):
    from datetime import datetime
    
    participation = get_object_or_404(Participation, pk=participation_id)

    if is_challenge_admin(request.user, participation.challenge):
        participation.status = PARTICIPATION_STATE.CONFIRMED
        participation.date_accepted = datetime.now() 
        participation.save()
        return redirect("challenge_detail", participation.challenge.pk)

    info = _("You don't have permission to perform this action.")
    return render_to_response('account_information.html', 
            RequestContext(request, {
                    "information": info,
                    }))

@login_required
def participation_reject(request, participation_id):
    return

@login_required
def comment_add(request):
    if request.method == "POST":
        challenge_id = request.POST["challenge_id"]
        comment_text = request.POST["comment"]
        
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
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if (request.user==comment.user or
            is_challenge_admin(request.user, comment.challenge)):
        comment.is_deleted = True
        comment.save()
        return redirect("challenge_detail", comment.challenge.pk)

    info = _("You don't have permission to perform this action.")
    return render_to_response('account_information.html', 
            RequestContext(request, {
                    "information": info,
                    }))
