from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader

from forms import ChallengeForm
from models import Challenge


@login_required
def challenge_create(request):
    if request.method == "POST":
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = Challenge.objects.create(
                    name = form.cleaned_data["name"],
                    description = form.cleaned_data["description"],
                    location = form.cleaned_data["location"],
                    duration = form.cleaned_data["duration"],
                    is_contact_person = form.cleaned_data["is_contact_person"],
                    contact_person = request.user,
                    is_alt_person = form.cleaned_data["is_alt_person"],
                    alt_person_fullname = form.cleaned_data[
                            "alt_person_fullname"],
                    alt_person_email = form.cleaned_data["alt_person_email"],
                    alt_person_phone = form.cleaned_data["alt_person_phone"],
                    start_date = form.cleaned_data["start_date"],
                    start_time = form.cleaned_data["start_time"],
                    alt_date = form.cleaned_data["alt_date"],
                    alt_time = form.cleaned_data["alt_time"],
                    organization = form.cleaned_data["organization"],
                    application = form.cleaned_data["application"],
                    min_participants = form.cleaned_data["min_participants"],
                    max_participants = form.cleaned_data["max_participants"],
                    latest_signup = form.cleaned_data["latest_signup"],
                    )

            return redirect("challenge_list")
    else:
        form = ChallengeForm()
    
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
