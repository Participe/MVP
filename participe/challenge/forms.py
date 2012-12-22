import os

from django import forms
from django.conf import settings
                             
from models import Challenge
import participe.core.html5_widgets as widgets


class ChallengeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChallengeForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pass

        self.fields["organization"].empty_label = None
        
    contact = forms.CharField(max_length=2)

    class Meta:
        model = Challenge
        fields = ["avatar", "name", "description", "location", "duration",
            "is_contact_person", "is_alt_person", "alt_person_fullname",
            "alt_person_email", "alt_person_phone", "start_date", "start_time",
            "alt_date", "alt_time", "organization", "application",
            "min_participants", "max_participants", "latest_signup",
            ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Challenge name"}),
            "description": forms.Textarea(attrs={
                    "cols": 25, "rows": 5,
                    "placeholder": "Challenge description"}),
            "location": forms.TextInput(attrs={"placeholder": "Location"}),
            "duration": widgets.NumberInput(attrs={
                    'min': '1', 'max': '10', 'step': '1',
                    "class": "input-mini"}),
            
            "alt_person_fullname": forms.TextInput(attrs={
                    "placeholder": "Full name"}),
            "alt_person_email": forms.TextInput(attrs={
                    "placeholder": "E-mail"}),
            "alt_person_phone": forms.TextInput(attrs={
                    "placeholder": "Phone number"}),

            "start_date": widgets.DateInput(attrs={"class": "input-small"}),
            "start_time": widgets.TimeInput(attrs={"class": "input-mini"}),
            "alt_date": widgets.DateInput(attrs={"class": "input-small"}),
            "alt_time": widgets.TimeInput(attrs={"class": "input-mini"}),
            
            "application": forms.RadioSelect(),

            "min_participants": widgets.NumberInput(attrs={
                    'min': '1', 'max': '10', 'step': '1',
                    "class": "input-mini"}),
            "max_participants": widgets.NumberInput(attrs={
                    'min': '1', 'max': '999999', 'step': '1',
                    "class": "input-mini"}),
            
            "latest_signup": forms.RadioSelect(),
            }

    def clean_avatar(self):
        data = self.cleaned_data['avatar']

        if data:
            if settings.AVATAR_ALLOWED_FILE_EXTS:
                (root, ext) = os.path.splitext(data.name.lower())
                if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                    raise forms.ValidationError(
                            u"%(ext)s is an invalid file extension. Authorized extensions are : %(valid_exts_list)s" % 
                            {'ext': ext, 'valid_exts_list': ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)}) 
            if data.size > settings.AVATAR_MAX_SIZE:
                raise forms.ValidationError(
                        u"Your file is too big (%(size)s), the maximum allowed size is %(max_valid_size)s" %
                        {'size': filesizeformat(data.size), 'max_valid_size': filesizeformat(settings.AVATAR_MAX_SIZE)})
        return self.cleaned_data['avatar']      

    def clean_duration(self):
        if self.cleaned_data["duration"] < 1:
            raise forms.ValidationError("Value should be greater or equal 1")
        return self.cleaned_data["duration"]

    def clean_min_participants(self):
        if self.cleaned_data["min_participants"] < 1:
            raise forms.ValidationError("Value should be greater or equal 1")
        return self.cleaned_data["min_participants"]

    def clean_max_participants(self):
        if self.cleaned_data["max_participants"] < 1:
            raise forms.ValidationError("Value should be greater or equal 1")
        return self.cleaned_data["max_participants"]

    def clean_contact(self):
        if self.cleaned_data["contact"] == 'me':
            self.cleaned_data["is_contact_person"] = True
            self.cleaned_data["is_alt_person"] = False
        elif self.cleaned_data["contact"] == 'he':
            self.cleaned_data["is_contact_person"] = False
            self.cleaned_data["is_alt_person"] = True
        else:
            self._errors["contact"] = self.error_class(
                    ["This field is required.",])
            del self.cleaned_data["contact"]

        return self.cleaned_data["contact"]
    
    def clean(self):
        if self.cleaned_data["is_alt_person"] == True:
            if not self.cleaned_data["alt_person_fullname"]:
                self._errors["alt_person_fullname"] = self.error_class(
                        ["This field is required.",])
                del self.cleaned_data["alt_person_fullname"]
            if not self.cleaned_data["alt_person_email"]:
                self._errors["alt_person_email"] = self.error_class(
                        ["This field is required.",])
                del self.cleaned_data["alt_person_email"]
            if not self.cleaned_data["alt_person_phone"]:
                self._errors["alt_person_phone"] = self.error_class(
                        ["This field is required.",])
                del self.cleaned_data["alt_person_phone"]

        return self.cleaned_data
