from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from forms import ChallengeForm
from models import Challenge


@login_required
def challenge_create(request):
    form = ChallengeForm(
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
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    return render_to_response('challenge_detail.html',
            RequestContext(request, {'challenge': challenge}))
