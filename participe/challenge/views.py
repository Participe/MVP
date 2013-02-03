from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from templated_email import send_templated_mail

from forms import CreateChallengeForm, SignupChallengeForm
from models import Challenge, Participation
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

                    if challenge.application == "0":
                        send_templated_mail(
                            template_name="challenge_successful_signup",
                            from_email="from@example.com", 
                            recipient_list=[user.email,], 
                            context={
                                    "user": user,
                                    "challenge": challenge,
                                    },)
                    else:
                        # TODO Send notification to Chjallenge Admin?
                        pass
                    return redirect("challenge_detail", challenge.pk)
            ctx.update({"form": form})

    return render_to_response('challenge_detail.html',
            RequestContext(request, ctx))
