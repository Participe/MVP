from django import forms
from django.contrib.auth.models import User
from django.core.validators import email_re

from captcha.fields import CaptchaField

from models import UserProfile
from participe.core.countries import COUNTRIES
import participe.core.html5_widgets as widgets


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pass

        #self.fields["username"].required = False
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = False

        self.fields["first_name"].label = "first_name"
        self.fields["last_name"].label = "last_name"
        self.fields["email"].label = "email"
        self.fields["password"].label = "password"
        self.fields["retry"].label = "retry"
        
    retry = forms.CharField(widget=forms.PasswordInput(attrs={
            "min_length": 6, "max_length": 30, "placeholder": "Retry",
            "value": ""}))
    
    class Meta:
        model = User
        fields = [#"username",
            "first_name", "last_name", "email", "password",]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": widgets.EmailInput(attrs={"placeholder": "E-mail"}),
            "password": forms.PasswordInput(attrs={
                    "min_length": 6, "max_length": 30,
                    "placeholder": "Password"}),
            }
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        
        if not email_re.match(email):
            raise forms.ValidationError(
                    "Please, enter valid e-mail address.")

        # E-mail address should be unique
        try:
            u = User.objects.get(username=email)
            raise forms.ValidationError(
                    "Account with such e-mail address already exists.")
        except User.DoesNotExist:
            pass
            
        return self.cleaned_data["email"]
        
    def clean_retry(self):
       if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
           raise forms.ValidationError("Passwords don't match")
       return self.cleaned_data["retry"]

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pass

        self.fields["address_1"].label = "address_1"
        self.fields["address_2"].label = "address_2"
        self.fields["postal_code"].label = "postal_code"
        self.fields["city"].label = "city"
        self.fields["country"].label = "country"
        self.fields["birth_day"].label = "Birth day"
        self.fields["phone_number"].label = "phone_number"
        self.fields["receive_newsletter"].label = "Receive newsletters"
                
        # Override countries order in choice-list
        self.fields["country"].choices = COUNTRIES
        self.fields["country"].initial = "CH"

    captcha = CaptchaField()
    birth_day = forms.DateField(
            input_formats=("%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y",),
            widget=widgets.DateInput(attrs={"class": "input-small"}))

    class Meta:
        model = UserProfile
        fields = ["address_1", "address_2", "postal_code", "city", "country",
            #"gender",
            "birth_day", "phone_number", "receive_newsletter",]
        widgets = {
            "address_1": forms.TextInput(attrs={"placeholder": "Address 1"}),
            "address_2": forms.TextInput(attrs={"placeholder": "Address 2"}),
            "postal_code": forms.TextInput(attrs={
                    "placeholder": "Postal code"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "country": forms.Select(),
            #"gender": forms.Select(attrs={"class": "input-small"}),
            #"birth_day": widgets.DateInput(attrs={"class": "input-small"}),
            "phone_number": forms.TextInput(attrs={
                    "placeholder": "Phone number"}),
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
        
        #self.fields["username"].label = "username"
        self.fields["first_name"].label = "first_name"
        self.fields["last_name"].label = "last_name"
        self.fields["email"].label = "email"
        self.fields["address_1"].label = "address_1"
        self.fields["address_2"].label = "address_2"
        self.fields["postal_code"].label = "postal_code"
        self.fields["city"].label = "city"
        self.fields["country"].label = "country"
        self.fields["birth_day"].label = "Birth day"
        self.fields["phone_number"].label = "phone_number"
        self.fields["receive_newsletter"].label = "Receive newsletters"

    #username = forms.CharField(widget=forms.TextInput(attrs={
    #        "placeholder": "User name", "value": ""}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
            "placeholder": "First name", "value": ""}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
            "placeholder": "Last name", "value": ""}))
    email = forms.EmailField(widget=widgets.EmailInput(attrs={
            "placeholder": "E-mail", "value": ""}))

    class Meta:
        model = UserProfile
        fields = [#"username",
            "first_name", "last_name", "email",
            "address_1", "address_2", "postal_code", "city", "country",
            #"gender",
            "birth_day", "phone_number", "receive_newsletter",]
        widgets = {
            "address_1": forms.TextInput(attrs={"placeholder": "Address 1"}),
            "address_2": forms.TextInput(attrs={"placeholder": "Address 2"}),
            "postal_code": forms.TextInput(attrs={
                    "placeholder": "Postal code"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "country": forms.Select(),
            #"gender": forms.Select(attrs={"class": "input-small"}),
            "birth_day": widgets.DateInput(attrs={"class": "input-small"}),
            "phone_number": forms.TextInput(attrs={
                    "placeholder": "Phone number"}),
            }
        
    def save(self, commit=True):
        instance = super(UserEditForm, self).save(commit=False)
        instance.user = self.user
        
        if commit:
            instance.save()
            
class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            "min_length": 6, "max_length": 30, "placeholder": "Password",
            "value": ""}))
    retry = forms.CharField(widget=forms.PasswordInput(attrs={
            "min_length": 6, "max_length": 30, "placeholder": "Retry",
            "value": ""}))

    def clean_retry(self):
       if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
           raise forms.ValidationError("Passwords don't match")
       return self.cleaned_data["retry"]
