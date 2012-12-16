from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader

import json
import urllib

from templated_email import send_templated_mail
from social_auth.utils import setting

from forms import UserForm, UserProfileForm, ResetPasswordForm, UserEditForm
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
                    #gender = pform.cleaned_data["gender"],
                    birth_day = pform.cleaned_data["birth_day"],
                    phone_number = pform.cleaned_data["phone_number"],
                    receive_newsletter = pform.cleaned_data[
                            "receive_newsletter"],
                    )

            # Let it be here. Instant log-in after sign-up
            user = authenticate(
                    username=uform.cleaned_data["username"],
                    password=uform.cleaned_data["password"])
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

                return render_to_response(
                        'account_confirmation_email.html', 
                        RequestContext(request, {
                                "address": user.email,
                                }))
            except:
                return HttpResponseRedirect('/')
    else:
        uform = UserForm()
        pform = UserProfileForm()

    #XXX Point-blank auth. Uncomment for testing
    """
    fb_profile = None
    if request.method == "GET":
        access_token = request.GET.get('access_token')
        if access_token:
            fb_profile = urllib.urlopen('https://graph.facebook.com/me?access_token=%s' % access_token)
            fb_profile = json.load(fb_profile)
                
            uform.fields['username'].initial = fb_profile['username']
            uform.fields['first_name'].initial = fb_profile['first_name']
            uform.fields['last_name'].initial = fb_profile['last_name']
            uform.fields['email'].initial = fb_profile['email']
    """
             
    return render_to_response('account_signup.html',
            RequestContext(request, {
                    'uform': uform,
                    'pform': pform,
                    #XXX Point-blank auth. Uncomment for testing
                    #'fb_app_id': setting('FACEBOOK_APP_ID'),
                    #'app_scope': ",".join(setting('FACEBOOK_EXTENDED_PERMISSIONS')),
                    #'fb_profile': fb_profile,
                    }))

def account_list(request):
    accounts = User.objects.all()

    return render_to_response('account_list.html',
            RequestContext(request, {'accounts': accounts}))

def view_profile(request, user_id):
    account = get_object_or_404(User, pk=user_id)
    
    #TODO Enhance this behaviour
    try:
        profile = get_object_or_404(UserProfile, user=account)
    except:
        profile = None
    
    return render_to_response('account_foreignprofile.html',
            RequestContext(request, {
                    "account": account,
                    "profile": profile,
                    }))    

@login_required
def view_myprofile(request):
    user = request.user
    
    #TODO Enhance this behaviour
    try:
        profile = get_object_or_404(UserProfile, user=user)
    except:
        profile = None
    
    return render_to_response('account_myprofile.html',
            RequestContext(request, {
                    "user": user,
                    "profile": profile,
                    }))

@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except:
        profile = UserProfile()

    pform = UserEditForm(request.user, request.POST or None, instance=profile)

    if request.method == "POST":
        if pform.is_valid():
            # Update User
            user.first_name = pform.cleaned_data["first_name"]
            user.last_name = pform.cleaned_data["last_name"]
            user.email = pform.cleaned_data["email"]
            user.save()
                                
            pform.save()
            
            return HttpResponseRedirect('/accounts/profile/')
    
    return render_to_response('account_edit.html',
            RequestContext(request, {
                    "pform": pform,
                    }))
    
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

                return render_to_response(
                        'account_confirmation_email.html', 
                        RequestContext(request, {
                                "address": user.email,
                                }))
            except:
                return HttpResponseRedirect('/accounts/profile/')
    else:
        form = ResetPasswordForm()
    
    return render_to_response('account_reset_password.html',
            RequestContext(request, {
                    'form': form,
                    }))
