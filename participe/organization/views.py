from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader

from forms import OrganizationForm
from models import Organization


@login_required
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
    organizations = Organization.objects.all()
    return render_to_response('organization_list.html',
            RequestContext(request, {
                    'organizations': organizations,
                    }))

def organization_detail(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    affiliated_users = organization.affiliated_users.all()
    return render_to_response('organization_detail.html',
            RequestContext(request, {
                    'organization': organization,
                    'affiliated_users': affiliated_users,
                    }))
