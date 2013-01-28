from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.files.base import ContentFile
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils import timezone
from django.utils.translation import ugettext as _

import os
import datetime
import json
import random
import string
import urllib

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

from social_auth.utils import setting
from templated_email import send_templated_mail

from forms import (UserForm, UserProfileForm, ResetPasswordForm, UserEditForm,
        ChangeAvatarForm, AvatarCropForm)
from models import UserProfile
from participe.core.user_tests import user_profile_completed


def _attach_avatar(request, instance):
    try:
        avatar = request.FILES['avatar']
    except:
        return

    try:
        instance.avatar.save(avatar.name, avatar)
        instance.save()
    except:
        return

def _generate_confirmation_code():
    confirmation_code = ''.join(random.choice(
            string.ascii_uppercase + 
            string.digits +
            string.ascii_lowercase
            ) for x in range(33))
    return confirmation_code

def signup(request):
    uform = UserForm(request.POST or None, request.FILES or None)
    pform = UserProfileForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if uform.is_valid() and pform.is_valid():
            # Create User
            user = User.objects.create(
                    username = uform.cleaned_data["email"],
                    first_name = uform.cleaned_data["first_name"],
                    last_name = uform.cleaned_data["last_name"],
                    email = uform.cleaned_data["email"],
                    is_active=False,
                    )
            user.set_password(uform.cleaned_data["password"])
            user.save()
            
            confirmation_code = _generate_confirmation_code()
            
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
                    confirmation_code=confirmation_code,
                    )
            _attach_avatar(request, profile)

            """
            user = authenticate(
                    username=uform.cleaned_data["username"],
                    password=uform.cleaned_data["password"])
            login(request, user)
            """

            # Here and further, if "send_templated_email" will raise exception
            # (in general, if <user.email> not set), user will be redirected
            # to the "/home/" or other appropriate page. 
            confirmation_link = (
                    "http://%s/account/confirmation/%s/" %
                    (settings.DOMAIN_NAME, confirmation_code))
            try:
                send_templated_mail(
                        template_name="account_confirmation",
                        from_email="from@example.com", 
                        recipient_list=[user.email,], 
                        context={
                                "user": user,
                                "confirmation_link": confirmation_link,
                                },)
                return render_to_response('account_confirmation_email.html', 
                        RequestContext(request, {
                                "address": user.email,
                                }))
            except:
                return HttpResponseRedirect('/')

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

def email_confirmation(request, confirmation_code):
    try:
        profile = UserProfile.objects.get(confirmation_code=confirmation_code)
        user = User.objects.get(pk=profile.user.pk)

        if user.date_joined > (timezone.now() - datetime.timedelta(days=7)):
            # Instant log-in after confirmation
			user.is_active = True
			user.save()
			user.backend = "django.contrib.auth.backends.ModelBackend" 
			auth_login(request, user)
			
			info = _("You have successfuly confirmed your e-mail.")
			return render_to_response('account_information.html',
                    RequestContext(request, {
                            "information": info,
                            }))
        else:
            # Delete expired user profile and account
            profile.delete()
            user.delete()
            info = _("The link has been expired. Please, sign-up again.")
            return render_to_response('account_error.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
    except:
        raise Http404

def account_list(request):
    accounts = User.objects.all().filter(is_active=True)

    return render_to_response('account_list.html',
            RequestContext(request, {
                    'accounts': accounts
                    }))

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
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
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
            #user.email = pform.cleaned_data["email"]
            user.save()
            pform.save()
            
            return HttpResponseRedirect('/accounts/profile/view/')
    
    return render_to_response('account_edit.html',
            RequestContext(request, {
                    "pform": pform,
                    }))

@login_required
def delete_profile(request):
    if request.method == "POST":
        user = request.user
        [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id]

        try:
            profile = UserProfile.objects.get(user=user)
            profile.delete()
        except:
            pass

        user.delete()

        return HttpResponseRedirect('/')

    return render_to_response('account_delete.html',
            RequestContext(request, {}))

@login_required
def reset_password(request):
    form = ResetPasswordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data["password"])
            user.save()

            info = _("You have successfuly changed your password")
            return render_to_response('account_information.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
    return render_to_response('account_reset_password.html',
            RequestContext(request, {
                    'form': form,
                    }))

def notify_forgotten_password(request):
    if request.method == "POST":
        user = get_object_or_404(User, username=request.POST["renew"])
        profile = get_object_or_404(UserProfile, user=user)
        
        try:
            confirmation_code = _generate_confirmation_code()
            profile.confirmation_code = confirmation_code
            profile.save()
        
            confirmation_link = (
                    "http://%s/accounts/password/renew/%s/" %
                    (settings.DOMAIN_NAME, confirmation_code))
            send_templated_mail(
                    template_name="account_password_renew",
                    from_email="from@example.com", 
                    recipient_list=[user.email,], 
                    context={
                            "user": user,
                            "confirmation_link": confirmation_link,
                            },)
            info = _("Confirmation link to restore password were sent to address '%s'" % user.email)
            return render_to_response('account_information.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
        except:
            info = _("An error has been acquired.")
            return render_to_response('account_error.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
    return HttpResponseRedirect('/')

def renew_forgotten_password(request, confirmation_code):
    try:
        profile = UserProfile.objects.get(confirmation_code=confirmation_code)
        user = User.objects.get(pk=profile.user.pk)

        # Instant log-in after confirmation
        user.backend = "django.contrib.auth.backends.ModelBackend" 
        auth_login(request, user)
        return redirect("reset_password")
    except:
        raise Http404

# TODO On general success move this to separate application
@login_required
def change_avatar(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except:
        # If profile isn't filled up (i.e. doesn't exist), redirects user to
        # profile edit page
        return redirect("edit_profile")

    pform = ChangeAvatarForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if pform.is_valid():
            _attach_avatar(request, profile)
            return redirect("view_myprofile")
    
    return render_to_response('account_change_avatar.html', 
            RequestContext(request, {
                    "profile": profile,
                    "pform": pform,
                    }))

@login_required
def crop_avatar(request):
    form = AvatarCropForm(request.POST or None, request.FILES or None)
    profile = get_object_or_404(UserProfile, user=request.user)
    avatar = profile.avatar

    if avatar.width <= avatar.height:
        result = "width"
    else:
        result = "height"

    if settings.AVATAR_CROP_MAX_SIZE > max(avatar.width, avatar.height):
        AVATAR_CROP_MAX_SIZE = max(avatar.width, avatar.height)
    else:
        AVATAR_CROP_MAX_SIZE = settings.AVATAR_CROP_MAX_SIZE

    if request.method == "POST":
        try:
            orig = avatar.storage.open(avatar.name, 'rb').read()
            image = Image.open(StringIO(orig))
        except IOError:
            return
        form = AvatarCropForm(image, request.POST)

        if form.is_valid():
            top = int(form.cleaned_data["top"])
            left = int(form.cleaned_data["left"])
            right = int(form.cleaned_data["right"])
            bottom = int(form.cleaned_data["bottom"])

            box = [left, top, right, bottom]
            (w, h) = image.size
            if result=="width":
                box = map(lambda x: x*h/AVATAR_CROP_MAX_SIZE, box)
            else:
                box = map(lambda x: x*w/AVATAR_CROP_MAX_SIZE, box)

            image = image.crop(box)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            thumb = StringIO()
            image.save(thumb, settings.AVATAR_THUMB_FORMAT, 
                    quality=settings.AVATAR_THUMB_QUALITY)
            thumb_file = ContentFile(thumb.getvalue())

            base_name, ext = os.path.splitext(avatar.name)
            profile.avatar = avatar.storage.save(
                    "%s_cropped%s" % (base_name, ext), thumb_file)
            profile.save()

            return redirect("view_myprofile")

    return render_to_response("account_crop_avatar.html", 
            RequestContext(request, {
                    'AVATAR_CROP_MAX_SIZE': AVATAR_CROP_MAX_SIZE,
                    'dim': result,
                    'avatar': avatar,
                    'form': form
                    }))
