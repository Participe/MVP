import os

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import email_re
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _

from captcha.fields import CaptchaField

from models import UserProfile
from participe.core.countries import COUNTRIES
import participe.core.html5_widgets as widgets


class LoginForm(forms.Form):
    username = forms.CharField(
            label=_("E-mail"),
            widget=forms.TextInput(
                    attrs={"placeholder": _("E-mail"), "value": ""}))
    password = forms.CharField(
            label=_("Password"),
            widget=forms.PasswordInput(
                    attrs={"min_length": 6, "max_length": 30,
                            "placeholder": _("Password"), "value": ""}))
    remember_me = forms.BooleanField(label=_("Remember me"), required=False)

    def add_non_field_error(self, message):
        error_list = self.errors.setdefault(NON_FIELD_ERRORS, ErrorList())
        error_list.append(message)

class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pass

        #self.fields["username"].required = False
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = False

        self.fields["first_name"].label = _("First name")
        self.fields["last_name"].label = _("Last name")
        self.fields["email"].label = _("Email")
        self.fields["password"].label = _("Password")
        self.fields["retry"].label = _("Password again")
        
    retry = forms.CharField(
            widget=forms.PasswordInput(
                    attrs={"min_length": 6, "max_length": 30,
                            "placeholder": _("Retry"), "value": ""}))
    
    class Meta:
        model = User
        fields = [#"username",
            "first_name", "last_name", "email", "password",]
        widgets = {
            "first_name": forms.TextInput(
                    attrs={"placeholder": _("First name")}),
            "last_name": forms.TextInput(
                    attrs={"placeholder": _("Last name")}),
            "email": widgets.EmailInput(
                    attrs={"placeholder": _("E-mail")}),
            "password": forms.PasswordInput(
                    attrs={"min_length": 6, "max_length": 30,
                            "placeholder": _("Password")}),
            }
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        
        if not email_re.match(email):
            raise forms.ValidationError(
                    _("Please, enter valid e-mail address."))

        # E-mail address should be unique
        try:
            u = User.objects.get(username=email)
            raise forms.ValidationError(
                    _("Account with such e-mail address already exists."))
        except User.DoesNotExist:
            pass
            
        return self.cleaned_data["email"]
        
    def clean_retry(self):
       if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
           raise forms.ValidationError(_("Passwords don't match"))
       return self.cleaned_data["retry"]

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pass

        self.fields["address_1"].required = True
        self.fields["postal_code"].required = True
        self.fields["city"].required = True
        self.fields["country"].required = True
        self.fields["birth_day"].required = True

        self.fields["address_1"].label = _("Street and house number")
        self.fields["address_2"].label = _("Additional address info")
        self.fields["postal_code"].label = _("Postal Code")
        self.fields["city"].label = _("City")
        self.fields["country"].label = _("Country")
        self.fields["birth_day"].label = _("Date of birth")
        self.fields["phone_number"].label = _("Phone number")
        self.fields["privacy_mode"].label = _("Privacy mode")
        self.fields["receive_newsletter"].label =\
                _("I want to get the Participe newsletter")
                
        # Override countries order in choice-list
        self.fields["country"].choices = COUNTRIES
        self.fields["country"].initial = "CH"

    captcha = CaptchaField()
    birth_day = forms.DateField(
            input_formats=("%d.%m.%Y",),
            widget=forms.DateInput(
                    format="%d.%m.%Y",
                    attrs={"class": "input-small"}))

    class Meta:
        model = UserProfile
        fields = ["avatar",
            "address_1", "address_2", "postal_code", "city", "country",
            #"gender",
            "birth_day", "phone_number", "receive_newsletter", "privacy_mode",
            ]
        widgets = {
            "address_1": forms.TextInput(
                    attrs={"placeholder": _("Address 1")}),
            "address_2": forms.TextInput(
                    attrs={"placeholder": _("Address 2")}),
            "postal_code": forms.TextInput(
                    attrs={"placeholder": _("Postal code")}),
            "city": forms.TextInput(
                    attrs={"placeholder": _("City")}),
            "country": forms.Select(),
            #"gender": forms.Select(attrs={"class": "input-small"}),
            #"birth_day": widgets.DateInput(attrs={"class": "input-small"}),
            "phone_number": forms.TextInput(
                    attrs={"placeholder": _("Phone number")}),
            "privacy_mode": forms.RadioSelect(),
            }
            
class UserEditForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.user = user
        
        #self.fields['username'].initial = user.username
        #self.fields['username'].widget.attrs['class'] = 'disabled'
        #self.fields['username'].widget.attrs['readonly'] = True
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email
        self.fields['email'].required = False
        self.fields['email'].widget.attrs['class'] = 'disabled'
        self.fields['email'].widget.attrs['readonly'] = True
        
        self.fields["address_1"].required = True
        self.fields["postal_code"].required = True
        self.fields["city"].required = True
        self.fields["country"].required = True
        self.fields["birth_day"].required = True

        #self.fields["username"].label = "username"
        self.fields["first_name"].label = _("first_name")
        self.fields["last_name"].label = _("last_name")
        self.fields["email"].label = _("email")
        self.fields["address_1"].label = _("address_1")
        self.fields["address_2"].label = _("address_2")
        self.fields["postal_code"].label = _("postal_code")
        self.fields["city"].label = _("city")
        self.fields["country"].label = _("country")
        self.fields["birth_day"].label = _("Birth day")
        self.fields["phone_number"].label = _("phone_number")
        self.fields["privacy_mode"].label = _("Privacy mode")
        self.fields["receive_newsletter"].label =\
                _("I want to get the Participe newsletter")

        # Override countries order in choice-list
        self.fields["country"].choices = COUNTRIES
        self.fields["country"].initial = "CH"

    #username = forms.CharField(widget=forms.TextInput(attrs={
    #        "placeholder": "User name", "value": ""}))
    first_name = forms.CharField(
            widget=forms.TextInput(
                    attrs={"placeholder": _("First name"), "value": ""}))
    last_name = forms.CharField(
            widget=forms.TextInput(
                    attrs={"placeholder": _("Last name"), "value": ""}))
    email = forms.EmailField(
            widget=widgets.EmailInput(
                    attrs={"placeholder": _("E-mail"), "value": ""}))
    birth_day = forms.DateField(
            input_formats=("%d.%m.%Y",),
            widget=forms.DateInput(
                    format="%d.%m.%Y",
                    attrs={"class": "input-small"}))

    class Meta:
        model = UserProfile
        fields = [#"username",
            "first_name", "last_name", "email",
            "address_1", "address_2", "postal_code", "city", "country",
            #"gender",
            "birth_day", "phone_number", "receive_newsletter", "privacy_mode",
            ]
        widgets = {
            "address_1": forms.TextInput(
                    attrs={"placeholder": _("Address 1")}),
            "address_2": forms.TextInput(
                    attrs={"placeholder": _("Address 2")}),
            "postal_code": forms.TextInput(
                    attrs={"placeholder": _("Postal code")}),
            "city": forms.TextInput(
                    attrs={"placeholder": _("City")}),
            "country": forms.Select(),
            #"gender": forms.Select(attrs={"class": "input-small"}),
            #"birth_day": widgets.DateInput(attrs={"class": "input-small"}),
            "phone_number": forms.TextInput(
                    attrs={"placeholder": _("Phone number")}),
            "privacy_mode": forms.RadioSelect(),
            }
        
    def save(self, commit=True):
        instance = super(UserEditForm, self).save(commit=False)
        instance.user = self.user
        
        if commit:
            instance.save()
            
class ResetPasswordForm(forms.Form):
    password = forms.CharField(
            widget=forms.PasswordInput(
                    attrs={"min_length": 6, "max_length": 30,
                            "placeholder": _("Password"), "value": ""}))
    retry = forms.CharField(
            widget=forms.PasswordInput(
                    attrs={"min_length": 6, "max_length": 30,
                            "placeholder": _("Retry"), "value": ""}))

    def clean_retry(self):
       if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
           raise forms.ValidationError(_("Passwords don't match"))
       return self.cleaned_data["retry"]

class RestorePasswordForm(forms.Form):
    email = forms.EmailField(
            widget=widgets.EmailInput(
                    attrs={"placeholder": _("E-mail"), "value": ""}))

    def clean_email(self):
        email = self.cleaned_data["email"]
        
        if not email_re.match(email):
            raise forms.ValidationError(
                    _("Please, enter valid e-mail address."))

        # E-mail address should exist
        try:
            u = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(
                    _("Account with such e-mail address does not exist."))
        return self.cleaned_data["email"]

# TODO On general success move this to separate application
# TODO Here and elsewhere, move "clean_avatar" code to "validators"
class ChangeAvatarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChangeAvatarForm, self).__init__(*args, **kwargs)
    
    avatar = forms.ImageField()
    
    def clean_avatar(self):
        data = self.cleaned_data['avatar']

        if data:
            if settings.AVATAR_ALLOWED_FILE_EXTS:
                (root, ext) = os.path.splitext(data.name.lower())
                if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                    raise forms.ValidationError(
                            "%(ext)s is an invalid file extension. "
                            "Authorized extensions are : %(valid_exts_list)s" % 
                            {'ext': ext,
                            'valid_exts_list':
                                ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)}) 
            if data.size > settings.AVATAR_MAX_SIZE:
                raise forms.ValidationError(
                        u"Your file is too big (%(size)s), the maximum "
                        "allowed size is %(max_valid_size)s" %
                        {'size': filesizeformat(data.size),
                        'max_valid_size':
                            filesizeformat(settings.AVATAR_MAX_SIZE)})
        return self.cleaned_data['avatar']      

class AvatarCropForm(forms.Form):
    top = forms.IntegerField(widget=forms.HiddenInput, required=False)
    left = forms.IntegerField(widget=forms.HiddenInput, required=False)
    right = forms.IntegerField(widget=forms.HiddenInput, required=False)
    bottom = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, image=None, *args, **kwargs):
        self.image = image
        super(AvatarCropForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.cleaned_data.get('top') and \
            not self.cleaned_data.get('bottom') and \
            not self.cleaned_data.get('left')  and \
            not self.cleaned_data.get('right'):
            raise forms.ValidationError(_('You need to make a selection'))

        elif self.cleaned_data.get('right') is None \
            or self.cleaned_data.get('left') is None \
            or int(self.cleaned_data.get('right')) - \
            int(self.cleaned_data.get('left')) < settings.AVATAR_CROP_MIN_SIZE:
            raise forms.ValidationError(
                    _("You must select a portion of the image with "
                    "a minimum of %(size)dx%(size)d pixels.") 
                    % {'size': settings.AVATAR_CROP_MIN_SIZE})

        return self.cleaned_data
