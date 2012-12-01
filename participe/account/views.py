from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader

from forms import UserForm, UserProfileForm
from models import UserProfile

def signup(request):
    if request.method == "POST":
        uform = UserForm(request.POST)
        pform = UserProfileForm(request.POST)
        if uform.is_valid() and pform.is_valid():
            # Create User
            user = User.objects.create(
                    username = uform.cleaned_data["username"],
                    first_name = uform.cleaned_data["first_name"],
                    last_name = uform.cleaned_data["last_name"],
                    email = uform.cleaned_data["email"],
                    )
            user.set_password(uform.cleaned_data["password"])
            user.save()
            
            # Create User Profile
            profile = UserProfile.objects.create(
                    user = user,
                    address_1 = pform.cleaned_data["address_1"],
                    address_2 = pform.cleaned_data["address_2"],
                    postal_code = pform.cleaned_data["postal_code"],
                    city = pform.cleaned_data["city"],
                    country = pform.cleaned_data["country"],
                    phone_number = pform.cleaned_data["phone_number"],
                    #receive_newsletter = pform.cleaned_data["receive_newsletter"],
                    birth_day = pform.cleaned_data["birth_day"],
                    )
            
            # TODO Change redirect in future
            return HttpResponseRedirect('/home/')
    else:
        uform = UserForm()
        pform = UserProfileForm()
    
    return render_to_response('signup.html', RequestContext(request, {'uform': uform, 'pform': pform}))

@login_required
def profile(request):
    return render_to_response('profile.html', RequestContext(request))
