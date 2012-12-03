from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader

from templated_email import send_templated_mail

from forms import UserForm, UserProfileForm, ResetPasswordForm
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
                    gender = pform.cleaned_data["gender"],
                    birth_day = pform.cleaned_data["birth_day"],
                    phone_number = pform.cleaned_data["phone_number"],
                    receive_newsletter = pform.cleaned_data["receive_newsletter"],
                    )

            # Let it be here. Instant log-in after sign-up
            user = authenticate(username=uform.cleaned_data["username"], password=uform.cleaned_data["password"])
            login(request, user)
         
            # Here and further, if "send_templated_email" will raise exception
            # (in general, if <user.email> not set), user will be redirected
            # to the "/home/" or other appropriate page. 
            try:
                send_templated_mail(
                        template_name="account_successful_signup",
                        from_email="from@example.com", 
                        recipient_list=[user.email,], 
                        context={"user": user},)
                return render_to_response('account_confirmation_email.html', RequestContext(request, {"address": user.email}))
            except:
                return HttpResponseRedirect('/home/')
    else:
        uform = UserForm()
        pform = UserProfileForm()
    
    return render_to_response('account_signup.html', RequestContext(request, {'uform': uform, 'pform': pform}))

@login_required
def profile(request):
    return render_to_response('account_profile.html', RequestContext(request))
    
@login_required
def reset_password(request):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data["password"])
            user.save()
    
            try:
                send_templated_mail(
                        template_name="account_successful_reset_password",
                        from_email="from@example.com", 
                        recipient_list=[user.email,], 
                        context={"user": user},)
                return render_to_response('account_confirmation_email.html', RequestContext(request, {"address": user.email}))
            except:
                return HttpResponseRedirect('/accounts/profile/')
    else:
        form = ResetPasswordForm()
    
    return render_to_response('account_reset_password.html', RequestContext(request, {'form': form}))
    
