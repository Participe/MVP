from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField

from participe.organization.models import Organization


application_choices = [
    ("0", "Not required: participation by application order"),
    ("1", "Confirmation of participation required"),
    ]
    
latest_signup_choices = [
    ("0", "last minute"),
    ("1", "one week before"),
    ("2", "other"),
    ]
    
class Challenge(models.Model):
    avatar = ThumbnailerImageField(upload_to='img/challenges', blank=True)
    name = models.CharField(max_length=80)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=80, null=True, blank=True)
    duration = models.PositiveIntegerField(default=1, null=True, blank=True)

    # Even if primary contact person isn't set, despite everything,
    # value 'contact_person' can be used to identify who has created challenge
    is_contact_person = models.BooleanField(default=True)
    contact_person = models.ForeignKey(User, related_name="contact_chl_set")
    
    is_alt_person = models.BooleanField(default=False)
    alt_person_fullname = models.CharField(
            max_length=80, null=True, blank=True)
    alt_person_email = models.EmailField(max_length=80, null=True, blank=True)
    alt_person_phone = models.CharField(max_length=15, blank=True, default='')
    
    start_date = models.DateField()
    start_time = models.TimeField()
    alt_date = models.DateField(null=True, blank=True)
    alt_time = models.TimeField(null=True, blank=True)
    
    organization = models.ForeignKey(Organization, null=True)
    application = models.CharField(
            max_length=2, choices=application_choices, default="0")
    min_participants = models.PositiveIntegerField(
            default=1, null=True, blank=True)
    max_participants = models.PositiveIntegerField(
            default=1, null=True, blank=True)
    latest_signup = models.CharField(
            max_length=2, choices=latest_signup_choices, default="0")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'challenge'
        verbose_name_plural = 'challenges'
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

