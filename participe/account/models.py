from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from django_countries import CountryField


gender_choices = [
    ("M", _("Male")),
    ("F", _("Female")),
    ]

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=_("User"))
    #avatar =
    #description =
            
    address_1 = models.CharField(max_length=80, verbose_name=_("Address 1"))
    address_2 = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("Address 2"))
    postal_code = models.PositiveIntegerField(verbose_name=_("Postal Code"))
    city = models.CharField(max_length=80, verbose_name=_("City"))
    country = CountryField(verbose_name=_("Country"))

    gender = models.CharField(
            max_length=2, choices=gender_choices, default="M",
            verbose_name=_("Gender"))
    
    birth_day = models.DateField(verbose_name=_("Birthday"))
    phone_number = models.CharField(
            max_length=15, blank=True, default='',
            verbose_name=_("Phone Number"))
    receive_newsletter = models.BooleanField(
            default=False, verbose_name=_("Receive Newsletters"))
    
    confirmation_code = models.CharField(max_length=33, null=True, blank=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        ordering = ['user__first_name', 'user__last_name',]

    def __unicode__(self):
        return unicode(self.user)

    #def get_absolute_url(self):
    #    return reverse('participe.account.views.profile', args=[str(self.id)])
    
    @property
    def is_completed(self):
        if (self.address_1 and self.postal_code and self.city and self.country
                and self.birth_day):
            return True
        return False
