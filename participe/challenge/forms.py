from django import forms

from models import Challenge
import participe.core.html5_widgets as widgets


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ["name", "description", "location", "duration",
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
                    'min': '1', 'max': '10', 'step': '1',
                    "class": "input-mini"}),
            
            "latest_signup": forms.RadioSelect(),
            }
