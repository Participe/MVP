import os
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
                 
from models import (Challenge, Participation, CHALLENGE_MODE,
        PARTICIPATION_STATE)
import participe.core.html5_widgets as widgets


class CreateChallengeForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(CreateChallengeForm, self).__init__(*args, **kwargs)
        self.user = user
        
        if self.instance and self.instance.pk:
            pass

        organizations = self.user.organization_set.all().order_by("name")
        self.fields["organization"].required = False
        if organizations:
            #self.fields["organization"].empty_label = None
            self.fields["organization"].queryset = organizations
            self.fields["organization"].initial = organizations[0]
        else:
            #self.fields["organization"].required = False
            self.fields["organization"].widget = \
                    self.fields["organization"].hidden_widget()

        self.contact_choices = [
            ("me", "%s (%s)" % (self.user.get_full_name(), self.user.email)),
            ("he", _("Affiliate different person")),]
        self.fields["contact"].choices = self.contact_choices
        self.fields["contact"].initial = "me"
         
    contact = forms.ChoiceField(
            widget=forms.RadioSelect())
    start_date = forms.DateField(
            input_formats=("%d.%m.%Y",),
            widget=forms.DateInput(
                    format="%d.%m.%Y",
                    attrs={"class": "input-small"}))

    class Meta:
        model = Challenge
        fields = ["avatar", "name", "description", "location", "duration",
            "is_contact_person", "is_alt_person", "alt_person_fullname",
            "alt_person_email", "alt_person_phone", "start_date", "start_time",
            "organization", "application",
            ]
        widgets = {
            "name": forms.TextInput(
                    attrs={"placeholder": _("Challenge name")}),
            "description": forms.Textarea(
                    attrs={"cols": 25, "rows": 5,
                    "placeholder": _("Challenge description")}),
            "location": forms.TextInput(
                    attrs={"placeholder": _("Location")}),
            "duration": widgets.NumberInput(
                    attrs={'min': '1', 'max': '10', 'step': '1',
                            "class": "input-mini"}),
            
            "alt_person_fullname": forms.TextInput(
                    attrs={"placeholder": _("Full name")}),
            "alt_person_email": forms.TextInput(
                    attrs={"placeholder": _("E-mail")}),
            "alt_person_phone": forms.TextInput(
                    attrs={"placeholder": _("Phone number")}),

            #"start_date": widgets.DateInput(attrs={"class": "input-small"}),
            "start_time": widgets.TimeInput(
                    attrs={"class": "input-mini"}),

            "application": forms.RadioSelect(),
            }

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

    def clean_duration(self):
        if self.cleaned_data["duration"] < 1:
            raise forms.ValidationError(
                    _("Value should be greater or equal 1"))
        return self.cleaned_data["duration"]

    def clean_contact(self):
        if self.cleaned_data["contact"] == 'me':
            self.cleaned_data["is_contact_person"] = True
            self.cleaned_data["is_alt_person"] = False
        elif self.cleaned_data["contact"] == 'he':
            self.cleaned_data["is_contact_person"] = False
            self.cleaned_data["is_alt_person"] = True
        else:
            self._errors["contact"] = self.error_class(
                    [_("This field is required."),])
            del self.cleaned_data["contact"]
        return self.cleaned_data["contact"]
    
    def clean(self):
        if self.cleaned_data["is_alt_person"] == True:
            if not self.cleaned_data["alt_person_fullname"]:
                self._errors["alt_person_fullname"] = self.error_class(
                        [_("This field is required."),])
                del self.cleaned_data["alt_person_fullname"]
            if not self.cleaned_data["alt_person_email"]:
                self._errors["alt_person_email"] = self.error_class(
                        [_("This field is required."),])
                del self.cleaned_data["alt_person_email"]
            if not self.cleaned_data["alt_person_phone"]:
                self._errors["alt_person_phone"] = self.error_class(
                        [_("This field is required."),])
                del self.cleaned_data["alt_person_phone"]
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(CreateChallengeForm, self).save(commit=False)
        instance.contact_person = self.user
        
        if commit:
            instance.save()

class EditChallengeForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(EditChallengeForm, self).__init__(*args, **kwargs)
        self.user = user

        self.fields['name'].widget.attrs['class'] = 'disabled'
        self.fields['name'].widget.attrs['readonly'] = True

        self.contact_choices = [
            ("me", "%s (%s)" % (self.instance.contact_person.get_full_name(),
                    self.instance.contact_person.email)),
            ("he", _("Affiliate different person")),]
        self.fields["contact"].choices = self.contact_choices
        if self.instance.is_contact_person:
            self.fields["contact"].initial = "me"
        else:
            self.fields["contact"].initial = "he"
         
    contact = forms.ChoiceField(
            widget=forms.RadioSelect())
    start_date = forms.DateField(
            input_formats=("%d.%m.%Y",),
            widget=forms.DateInput(
                    format="%d.%m.%Y",
                    attrs={"class": "input-small"}))

    class Meta:
        model = Challenge
        fields = ["avatar", "name", "description",
            "is_contact_person", "is_alt_person", "alt_person_fullname",
            "alt_person_email", "alt_person_phone", "start_date", "start_time",
            "application", "deleted_reason",
            ]
        widgets = {
            "description": forms.Textarea(
                    attrs={"cols": 25, "rows": 5,
                    "placeholder": _("Challenge description")}),
            "alt_person_fullname": forms.TextInput(
                    attrs={"placeholder": _("Full name")}),
            "alt_person_email": forms.TextInput(
                    attrs={"placeholder": _("E-mail")}),
            "alt_person_phone": forms.TextInput(
                    attrs={"placeholder": _("Phone number")}),
            #"start_date": widgets.DateInput(attrs={"class": "input-small"}),
            "start_time": widgets.TimeInput(
                    attrs={"class": "input-mini"}),
            "application": forms.RadioSelect(),
            "deleted_reason": forms.Textarea(
                    attrs={"placeholder": _("Reason for deletion "
                            "(at least 20 symbols)")}),
            }

    def clean_contact(self):
        if self.cleaned_data["contact"] == 'me':
            self.cleaned_data["is_contact_person"] = True
            self.cleaned_data["is_alt_person"] = False
        elif self.cleaned_data["contact"] == 'he':
            self.cleaned_data["is_contact_person"] = False
            self.cleaned_data["is_alt_person"] = True
        else:
            self._errors["contact"] = self.error_class(
                    [_("This field is required."),])
            del self.cleaned_data["contact"]
        return self.cleaned_data["contact"]
    
    def clean(self):
        if self.cleaned_data["is_alt_person"] == True:
            if not self.cleaned_data["alt_person_fullname"]:
                self._errors["alt_person_fullname"] = self.error_class(
                        [_("This field is required."),])
                del self.cleaned_data["alt_person_fullname"]
            if not self.cleaned_data["alt_person_email"]:
                self._errors["alt_person_email"] = self.error_class(
                        [_("This field is required."),])
                del self.cleaned_data["alt_person_email"]
            if not self.cleaned_data["alt_person_phone"]:
                self._errors["alt_person_phone"] = self.error_class(
                        [_("This field is required."),])
                del self.cleaned_data["alt_person_phone"]
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(EditChallengeForm, self).save(commit=False)
        if commit:
            instance.save()

class SignupChallengeForm(forms.ModelForm):
    def __init__(self, user, challenge, *args, **kwargs):
        super(SignupChallengeForm, self).__init__(*args, **kwargs)
        self.user = user
        self.challenge = challenge

        if self.instance and self.instance.pk:
            pass

    class Meta:
        model = Participation
        fields = ["application_text", "share_on_FB",]
        widgets = {
            "application_text": forms.Textarea(
                    attrs={"placeholder": _("Application text")}),
            }

    def save(self, commit=True):
        instance = super(SignupChallengeForm, self).save(commit=False)
        instance.user = self.user
        instance.challenge = self.challenge
        instance.date_created = datetime.now()
        
        # If instance if Free-for-All, set Participation status to "Confirmed"
        if self.challenge.application == CHALLENGE_MODE.CONFIRMATION_REQUIRED:
            instance.status = PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION
        
        if commit:
            instance.save()

class WithdrawSignupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WithdrawSignupForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            pass

    class Meta:
        model = Participation
        fields = ["cancellation_text",]
        widgets = {
            "application_text": forms.Textarea(
                    attrs={"placeholder": _("Reason for withdrawing")}),
            }

    def save(self, commit=True):
        instance = super(WithdrawSignupForm, self).save(commit=False)
        instance.status = PARTICIPATION_STATE.CANCELLED_BY_USER
        instance.date_cancelled = datetime.now()

        if commit:
            instance.save()
