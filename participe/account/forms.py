from django import forms
from django.contrib.auth.models import User

from models import UserProfile
import participe.core.html5_widgets as widgets


class UserForm(forms.ModelForm):
    retry = forms.CharField(widget=forms.PasswordInput(attrs={"min_length": 6, "max_length": 30, "placeholder": "Retry", "value": ""}))
    
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password",]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "User name"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": widgets.EmailInput(attrs={"placeholder": "E-mail"}),
            "password": forms.PasswordInput(attrs={"min_length": 6, "max_length": 30, "placeholder": "Password"}),
            }
    
    def clean_retry( self ):
       if ( self.cleaned_data["retry"] != self.cleaned_data.get( "password", "") ):
           raise forms.ValidationError("Passwords don't match")
       return self.cleaned_data["retry"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["address_1", "address_2", "postal_code", "city", "country",
            "gender", "birth_day", "phone_number", "receive_newsletter",]
        widgets = {
            "address_1": forms.TextInput(attrs={"placeholder": "Address 1"}),
            "address_2": forms.TextInput(attrs={"placeholder": "Address 2"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Postal code"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "country": forms.Select(),

            "gender": forms.RadioSelect(),
            
            "birth_day": widgets.DateInput(attrs={"class": "input-small"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "Phone number"}),
            }
