from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from easy_thumbnails.fields import ThumbnailerImageField

from participe.organization.models import Organization


application_choices = [
    ("0", _("Not required: participation by application order")),
    ("1", _("Confirmation of participation required")),
    ]
    
latest_signup_choices = [
    ("0", _("last minute")),
    ("1", _("one week before")),
    ("2", _("other")),
    ]
    
class Challenge(models.Model):
    avatar = ThumbnailerImageField(
            upload_to='img/challenges', verbose_name=_("Avatar"))
    name = models.CharField(max_length=80, verbose_name=_("Name"))
    description = models.TextField(
            null=True, blank=True, verbose_name=_("Description"))
    location = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("Location"))
    duration = models.PositiveIntegerField(
            default=1, null=True, blank=True, verbose_name=_("Duration"))

    # Even if primary contact person isn't set, despite everything,
    # value 'contact_person' can be used to identify who has created challenge
    is_contact_person = models.BooleanField(default=True)
    contact_person = models.ForeignKey(
            User, related_name="contact_chl_set",
            verbose_name=_("Contact Person"))
    
    is_alt_person = models.BooleanField(default=False)
    alt_person_fullname = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("Full name"))
    alt_person_email = models.EmailField(
            max_length=80, null=True, blank=True, verbose_name=_("E-mail"))
    alt_person_phone = models.CharField(
            max_length=15, blank=True, default='',
            verbose_name=_("Phone Number"))
    
    start_date = models.DateField(verbose_name=_("Start Date"))
    start_time = models.TimeField(verbose_name=_("Start Time"))
    alt_date = models.DateField(
            null=True, blank=True, verbose_name=_("Alternative Date"))
    alt_time = models.TimeField(
            null=True, blank=True, verbose_name=_("Alternative Time"))
    
    organization = models.ForeignKey(
            Organization, null=True, verbose_name=_("Organization"))
    application = models.CharField(
            max_length=2, choices=application_choices, default="0",
            verbose_name=_("Application"))
    min_participants = models.PositiveIntegerField(
            default=1, null=True, blank=True,
            verbose_name=_("Minimum Participants"))
    max_participants = models.PositiveIntegerField(
            default=1, null=True, blank=True,
            verbose_name=_("Maximum Participants"))
    latest_signup = models.CharField(
            max_length=2, choices=latest_signup_choices, default="0",
            verbose_name=_("Latest Sign-up"))
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('challenge')
        verbose_name_plural = _('challenges')
        ordering = ['name',]

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse(
                'participe.challenge.views.challenge_detail',
                args=[str(self.id)])
                
    @property
    def stat_application_name(self):
        for code, name in application_choices:
            if self.application == code:
                return name
        return ''

    @property
    def stat_latest_signup_name(self):
        for code, name in latest_signup_choices:
            if self.latest_signup == code:
                return name
        return ''

