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
        form = OrganizationForm(request.POST)
        if form.is_valid():
            Organization.objects.create(
                    name = form.cleaned_data["name"],
                    description = form.cleaned_data["description"],
                    address_1 = form.cleaned_data["address_1"],
                    address_2 = form.cleaned_data["address_2"],
                    postal_code = form.cleaned_data["postal_code"],
                    city = form.cleaned_data["city"],
                    country = form.cleaned_data["country"],
                    website = form.cleaned_data["website"],
                    video = form.cleaned_data["video"],
                    email = form.cleaned_data["email"],
                    is_contact_person = form.cleaned_data["is_contact_person"],
                    contact_person = request.user,
                    is_alt_person = form.cleaned_data["is_alt_person"],
                    alt_person_fullname = form.cleaned_data[
                            "alt_person_fullname"],
                    alt_person_email = form.cleaned_data["alt_person_email"],
                    alt_person_phone = form.cleaned_data["alt_person_phone"],
                    )

            return redirect("organization_list")
    else:
        form = OrganizationForm()
    
    return render_to_response('organization_create.html',
            RequestContext(request, {'form': form}))
    
def organization_list(request):
    organizations = Organization.objects.all()
    return render_to_response('organization_list.html',
            RequestContext(request, {'organizations': organizations}))

def organization_detail(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    return render_to_response('organization_detail.html',
            RequestContext(request, {'organization': organization}))
