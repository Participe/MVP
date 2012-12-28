import os

from django import forms
from django.conf import settings

from models import Organization
import participe.core.html5_widgets as widgets


class OrganizationForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.user = user
        
        if self.instance and self.instance.pk:
            pass

    class Meta:
        model = Organization
        fields = ["avatar", "name", "description", 
            "address_1", "address_2", "postal_code", "city", "country",
            "website", "video", "email", "is_contact_person", "is_alt_person",
            "alt_person_fullname", "alt_person_email", "alt_person_phone",
            ]
        widgets = {
            "name": forms.TextInput(attrs={
                    "placeholder": "Organization name"}),
            "description": forms.Textarea(attrs={
                    "cols": 25, "rows": 5,
                    "placeholder": "Organization description"}),

            "address_1": forms.TextInput(attrs={"placeholder": "Address 1"}),
            "address_2": forms.TextInput(attrs={"placeholder": "Address 2"}),
            "postal_code": forms.TextInput(attrs={
                    "placeholder": "Postal code"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            
            "website": widgets.URLInput(attrs={"placeholder": "Web site"}),
            "video": widgets.URLInput(attrs={
                    "placeholder": "Embedd video (link)"}),
            "email": widgets.EmailInput(attrs={
                    "placeholder": "Organization e-mail"}),

            "alt_person_fullname": forms.TextInput(attrs={
                    "placeholder": "Full name"}),
            "alt_person_email": forms.TextInput(attrs={
                    "placeholder": "E-mail"}),
            "alt_person_phone": forms.TextInput(attrs={
                    "placeholder": "Phone number"}),
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

    def save(self, commit=True):
        instance = super(OrganizationForm, self).save(commit=False)
        instance.contact_person = self.user
        
        if commit:
            instance.save()
