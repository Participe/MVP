from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from forms import OrganizationForm
from models import Organization

from participe.challenge.models import Challenge

from participe.core.user_tests import user_profile_completed


@login_required
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(
                request.user, request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect("organization_list")
    else:
        form = OrganizationForm(
                request.user, request.POST or None, request.FILES or None)
    return render_to_response('organization_create.html',
            RequestContext(request, {'form': form}))
    
def organization_list(request):
    organizations = Organization.objects.all().filter(
            is_deleted=False).order_by("name")
    return render_to_response('organization_list.html',
            RequestContext(request, {
                    'organizations': organizations,
                    }))

def organization_detail(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    affiliated_users = organization.affiliated_users.all()
    challenges = Challenge.objects.filter(organization=organization, is_deleted=False)
    return render_to_response('organization_detail.html',
            RequestContext(request, {
                    'organization': organization,
                    'affiliated_users': affiliated_users,
                    'challenges': challenges,
                    }))
