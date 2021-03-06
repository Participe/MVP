import os
import datetime
import random
import string
import hashlib

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.tokens import (default_token_generator as token_generator)
from django.contrib.auth.views import auth_login
from django.contrib.sessions.models import Session
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import (HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.utils.http import int_to_base36, base36_to_int
from django.utils.translation import ugettext as _

from auth_remember import remember_user
from social_auth.utils import setting
from templated_email import send_templated_mail

from forms import (LoginForm, UserForm, UserProfileForm, UserEditForm,
                   ResetPasswordForm, RestorePasswordForm, ChangeAvatarForm,
                   AvatarCropForm)
from models import UserProfile
from utils import get_user_participations, get_admin_challenges
from participe.account.models import PRIVACY_MODE
from participe.core.user_tests import user_profile_completed
from participe.challenge.models import (Challenge, Participation,
                                        CHALLENGE_STATUS, PARTICIPATION_STATE)
from participe.organization.models import Organization

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


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
                username=uform.cleaned_data["email"][:30],
                first_name=uform.cleaned_data["first_name"],
                last_name=uform.cleaned_data["last_name"],
                email=uform.cleaned_data["email"],
                is_active=False,
            )

            user.set_password(uform.cleaned_data["password"])
            user.save()

            confirmation_code = _generate_confirmation_code()

            # Create User Profile
            profile = UserProfile.objects.create(
                user=user,
                address_1=pform.cleaned_data["address_1"],
                address_2=pform.cleaned_data["address_2"],
                postal_code=pform.cleaned_data["postal_code"],
                city=pform.cleaned_data["city"],
                country=pform.cleaned_data["country"],
                birth_day=pform.cleaned_data["birth_day"],
                phone_number=pform.cleaned_data["phone_number"],
                receive_newsletter=pform.cleaned_data["receive_newsletter"],
                confirmation_code=confirmation_code,
            )
            _attach_avatar(request, profile)

            """
            user = authenticate(
                    username=uform.cleaned_data["username"],
                    password=uform.cleaned_data["password"])
            login(request, user)
            """

            DOMAIN_NAME = request.get_host()
            confirmation_link = (
                "http://%s/account/confirmation/%s/" %
                (DOMAIN_NAME, confirmation_code))

            send_templated_mail(
                template_name="account_confirmation",
                from_email=settings.EMAIL_SENDER,
                recipient_list=[user.email, ],
                context={
                    "user": user,
                    "confirmation_link": confirmation_link,
                    "subject": _("Welcome to Participe"),
                }, )

            return render_to_response('account_confirmation_email.html',
                                      RequestContext(request, {
                                          "address": user.email,
                                      }))

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

            return render_to_response('account_welcome.html',
                                      RequestContext(request, {
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


def account_login(request):
    form = LoginForm(request.POST or None)
    redirect_to = request.REQUEST.get('next', '')

    if request.method == "GET":
        if redirect_to and request.user.is_authenticated():
            return HttpResponseRedirect(redirect_to)

    if request.method == 'POST':
        if form.is_valid():
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            data = form.cleaned_data
            user = authenticate(
                username=data['username'],
                password=data['password'])

            if user:
                login(request, user)
                if data['remember_me']:
                    remember_user(request, user)
                return HttpResponseRedirect(redirect_to)
            else:
                form.add_non_field_error(
                    _("Sorry, you have entered wrong E-mail or Password"))

    return render_to_response('account_login.html',
                              RequestContext(request, {
                                  'form': form,
                                  'next': redirect_to,
                              }))

# Simple wrapper for django logout. Allows to logout Facebook together with
# Participe logout.
# As I supposed, FB.logout() works only if user were logged in using FB.init()
# and FB.login().
# There's another (but not easiest) way to implement such behaviour:
# 1. Pass to base template 'access_token' (via 'views' or 'template context');
# 2. In base template make request to
#    'https://www.facebook.com/logout.php?next=http://{%s}&access_token={%s}'
#    which will logout user from FB and redirect to, e.g.,
# 3. '/accounts/after_fb_logout/' which will logout user from Participe.
# This approach has a lot of intermediate steps and makes 'access_token'
# available for a criminal.
# So for now following is the best implementation.
@login_required
def account_logout(request, next_page):
    from django.contrib.auth.views import logout
    from social_auth.models import UserSocialAuth

    user = request.user
    DOMAIN_NAME = request.get_host() #settings.DOMAIN_NAME
    try:
        instance = UserSocialAuth.objects.filter(
            provider='facebook').get(user=user)
        access_token = instance.tokens["access_token"]
        fb_logout = (
            'https://www.facebook.com/logout.php?'
            'next=http://%s&access_token=%s' %
            (DOMAIN_NAME, access_token))
        response = logout(request, next_page=fb_logout)
    except:
        response = logout(request, next_page=next_page)
    return response


def view_profile(request, user_id):
    ctx = {}
    user = request.user

    account = get_object_or_404(User, pk=user_id)
    ctx.update({"account": account})

    #TODO Enhance this behaviour
    try:
        profile = get_object_or_404(UserProfile, user=account)
    except:
        profile = None
    ctx.update({"profile": profile})

    participations_current = Participation.objects.filter(
        user=account,
        challenge__is_deleted=False,
        status__in=[
            PARTICIPATION_STATE.CONFIRMED,
            PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
            PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT,
            PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION, ]
    )
    ctx.update({"participations_current": participations_current})

    participations_acknowledged = Participation.objects.filter(
        user=account,
        challenge__is_deleted=False,
        status=PARTICIPATION_STATE.ACKNOWLEDGED,
    )
    ctx.update({"participations_acknowledged": participations_acknowledged})

    participations_cancelled_by_user = Participation.objects.filter(
        user=account,
        challenge__is_deleted=False,
        status=PARTICIPATION_STATE.CANCELLED_BY_USER,
    )
    ctx.update({"participations_cancelled_by_user":
                    participations_cancelled_by_user})

    participations_cancelled_by_admin = Participation.objects.filter(
        user=account,
        challenge__is_deleted=False,
        status=PARTICIPATION_STATE.CANCELLED_BY_ADMIN,
    )
    ctx.update({"participations_cancelled_by_admin":
                    participations_cancelled_by_admin})

    affiliated_organizations = Organization.objects.filter(
        affiliated_users=account,
    )
    ctx.update({"affiliated_organizations": affiliated_organizations})

    if user.is_authenticated():
        admin_challenges = get_admin_challenges(user)
        desired_challenges = Challenge.objects.filter(
            pk__in=Participation.objects.filter(
                user=account,
                challenge__is_deleted=False,
                status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
            ).values_list("challenge_id", flat=True))

        # Related to viewer Challenges
        related_participated_challenges = [
            participation.challenge for participation in
            participations_current.exclude(
                status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
            )
            if participation.challenge in admin_challenges]
        ctx.update({"related_participated_challenges":
                        related_participated_challenges})

        related_desired_challenges = [
            challenge for challenge in desired_challenges
            if challenge in admin_challenges]
        ctx.update({"related_desired_challenges":
                        related_desired_challenges})

    ctx.update({"PRIVACY_MODE": PRIVACY_MODE})
    return render_to_response('account_foreignprofile.html',
                              RequestContext(request, ctx))


@login_required
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def view_myprofile(request):
    user = request.user

    user_participations = get_user_participations(user).order_by("challenge__start_date")

    user_participations_action_required = user_participations.filter(
        status=PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION
    )

    user_participations_upcoming = user_participations.filter(
        challenge__status=CHALLENGE_STATUS.UPCOMING,
        status__in=[
            PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
            PARTICIPATION_STATE.CONFIRMED
        ])

    user_participations_completed = user_participations.filter(
        challenge__status=CHALLENGE_STATUS.COMPLETED,
        status__in=[
            PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT,
            PARTICIPATION_STATE.ACKNOWLEDGED
        ])

    admin_challenges = get_admin_challenges(user).order_by("start_date")

    admin_challenges_action_required = admin_challenges.filter(
        Q(pk__in=Participation.objects.filter(
            status__in=[
                PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
            ]).values_list("challenge_id", flat=True)
        ) | Q(
            start_date__lt=datetime.date.today(),
            status=CHALLENGE_STATUS.UPCOMING
        )
    )

    admin_challenges_upcoming = admin_challenges.exclude(
        pk__in=Participation.objects.filter(
            status__in=[
                PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
            ]).values_list("challenge_id", flat=True)
    ).filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=datetime.date.today()
    )

    admin_challenges_completed = admin_challenges.exclude(
        pk__in=Participation.objects.filter(
            status=PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT
        ).values_list("challenge_id", flat=True)
    ).filter(
        status=CHALLENGE_STATUS.COMPLETED
    )

    participations_cancelled_by_user = Participation.objects.filter(
        user=user,
        challenge__is_deleted=False,
        status=PARTICIPATION_STATE.CANCELLED_BY_USER,
    )

    participations_cancelled_by_admin = Participation.objects.filter(
        user=user,
        challenge__is_deleted=False,
        status=PARTICIPATION_STATE.CANCELLED_BY_ADMIN,
    )

    try:
        profile = get_object_or_404(UserProfile, user=user)
    except:
        profile = None
    return render_to_response('account_myprofile.html',
                              RequestContext(request, {
                                  "user": user,
                                  "profile": profile,
                                  "user_participations":
                                      [(user_participations_action_required,
                                        _("Action required")),
                                       (user_participations_upcoming,
                                        _("Upcoming")),
                                       (user_participations_completed,
                                        _("Completed")), ],
                                  "admin_challenges":
                                      [(admin_challenges_action_required,
                                        _("Action required")),
                                       (admin_challenges_upcoming,
                                        _("upcoming")),
                                       (admin_challenges_completed,
                                        _("completed")), ],
                                  "participations_cancelled_by_user":
                                      participations_cancelled_by_user,
                                  "participations_cancelled_by_admin":
                                      participations_cancelled_by_admin,
                                  "PARTICIPATION_STATE": PARTICIPATION_STATE,
                                  "CHALLENGE_STATUS": CHALLENGE_STATUS,
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
                                  "profile": profile,
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
    form = RestorePasswordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = get_object_or_404(User, email=form.cleaned_data["email"])

            try:
                token = token_generator.make_token(user)
                DOMAIN_NAME = request.get_host()
                confirmation_link = (
                    "http://%s/accounts/password/renew/%s-%s/" %
                    (DOMAIN_NAME, int_to_base36(user.id), token))
                send_templated_mail(
                    template_name="account_password_renew",
                    from_email=settings.EMAIL_SENDER,
                    recipient_list=[user.email, ],
                    context={
                        "user": user,
                        "confirmation_link": confirmation_link,
                        "subject": _("New password for Participe")
                    }, )

                return render_to_response('account_restore_password_email_sent.html',
                                          RequestContext(request, {
                                              "email": user.email,
                                          }))
            except:
                info = _("An error has been acquired.")
                return render_to_response('account_error.html',
                                          RequestContext(request, {
                                              "information": info,
                                          }))
    return render_to_response('account_restore_password.html',
                              RequestContext(request, {
                                  'form': form,
                              }))


def renew_forgotten_password(request, uidb36=None, token=None):
    assert uidb36 is not None and token is not None

    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        # Instant log-in after confirmation
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth_login(request, user)
        return redirect("reset_password")
    else:
        info = _("An error has been acquired.")
        return render_to_response('account_error.html',
                                  RequestContext(request, {
                                      "information": info,
                                  }))

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
            if result == "width":
                box = map(lambda x: x * h / AVATAR_CROP_MAX_SIZE, box)
            else:
                box = map(lambda x: x * w / AVATAR_CROP_MAX_SIZE, box)

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
