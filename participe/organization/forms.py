from django import forms

from models import Organization
import participe.core.html5_widgets as widgets


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization

        fields = ["name", "description", 
            "address_1", "address_2", "postal_code", "city", "country",
            "website", "video", "email",
            "is_contact_person", "contact_person",
            "is_alt_person", "alt_person_fullname", "alt_person_email", "alt_person_phone",
            ]

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Organization name"}),
            "description": forms.Textarea(attrs={"cols": 25, "rows": 5, "placeholder": "Organization description"}),

            "address_1": forms.TextInput(attrs={"placeholder": "Address 1"}),
            "address_2": forms.TextInput(attrs={"placeholder": "Address 2"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Postal code"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            
            "website": widgets.URLInput(attrs={"placeholder": "Web site"}),
            "video": widgets.URLInput(attrs={"placeholder": "Embedd video (link)"}),
            "email": widgets.EmailInput(attrs={"placeholder": "Organization e-mail"}),

            "alt_person_fullname": forms.TextInput(attrs={"placeholder": "Full name"}),
            "alt_person_email": forms.TextInput(attrs={"placeholder": "E-mail"}),
            "alt_person_phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            }
