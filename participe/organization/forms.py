import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from models import Organization
from participe.core.countries import COUNTRIES
import participe.core.html5_widgets as widgets


class OrganizationForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.user = user
        
        if self.instance and self.instance.pk:
            pass

        # Override countries order in choice-list
        self.fields["country"].choices = COUNTRIES
        self.fields["country"].initial = "CH"

        self.contact_choices = [
            ("me", "%s (%s)" % (self.user.get_full_name(), self.user.email)),
            ("he", _("Affiliate different person")),]
        self.fields["contact"].choices = self.contact_choices
        self.fields["contact"].initial = "me"

    contact = forms.ChoiceField(
            widget=forms.RadioSelect())

    class Meta:
        model = Organization
        fields = ["avatar", "name", "description", 
            "address_1", "address_2", "postal_code", "city", "country",
            "website", "video", "email", "is_contact_person", "is_alt_person",
            "alt_person_fullname", "alt_person_email", "alt_person_phone",
            ]
        widgets = {
            "name": forms.TextInput(
                    attrs={"placeholder": _("Organization name")}),
            "description": forms.Textarea(
                    attrs={"cols": 25, "rows": 5,
                            "placeholder": _("Organization description")}),

            "address_1": forms.TextInput(
                    attrs={"placeholder": _("Address 1")}),
            "address_2": forms.TextInput(
                    attrs={"placeholder": _("Address 2")}),
            "postal_code": forms.TextInput(
                    attrs={"placeholder": _("Postal code")}),
            "city": forms.TextInput(
                    attrs={"placeholder": _("City")}),
            
            "website": widgets.URLInput(
                    attrs={"placeholder": _("Web site")}),
            "video": widgets.URLInput(
                    attrs={"placeholder": _("Embedd video (link)")}),
            "email": widgets.EmailInput(
                    attrs={"placeholder": _("Organization e-mail")}),

            "alt_person_fullname": forms.TextInput(
                    attrs={"placeholder": _("Full name")}),
            "alt_person_email": forms.TextInput(
                    attrs={"placeholder": _("E-mail")}),
            "alt_person_phone": forms.TextInput(
                    attrs={"placeholder": _("Phone number")}),
            }

    def clean_avatar(self):
        data = self.cleaned_data['avatar']

        if data:
            if settings.AVATAR_ALLOWED_FILE_EXTS:
                (root, ext) = os.path.splitext(data.name.lower())
                if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                    raise forms.ValidationError(
                            u"%(ext)s is an invalid file extension. "
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
        instance = super(OrganizationForm, self).save(commit=False)
        instance.contact_person = self.user
        
        if commit:
            instance.save()
            instance.affiliated_users.add(self.user)
