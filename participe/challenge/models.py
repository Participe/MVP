from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from easy_thumbnails.fields import ThumbnailerImageField

from participe.organization.models import Organization
from participe.enum import enum

CHALLENGE_MODE = enum(FREE_FOR_ALL = "0", CONFIRMATION_REQUIRED="1")

application_choices = [
    (CHALLENGE_MODE.FREE_FOR_ALL, _("Not required: participation by application order")),
    (CHALLENGE_MODE.CONFIRMATION_REQUIRED, _("Confirmation of participation required")),
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

    organization = models.ForeignKey(
            Organization, null=True, verbose_name=_("Organization"))
    application = models.CharField(
            max_length=2, choices=application_choices, default="0",
            verbose_name=_("Application"))

    is_deleted = models.BooleanField(default=False)
    deleted_reason = models.TextField(
            null=True, blank=True, verbose_name=_("Reason for deletion"))

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
                
    def get_edit_url(self):
        return reverse(
                'participe.challenge.views.challenge_edit',
                args=[str(self.id)])
                
    @property
    def stat_application_name(self):
        for code, name in application_choices:
            if self.application == code:
                return name
        return ''

    @property
    def get_waiting_count(self):
        return Participation.objects.all().filter(
                challenge=self, status="0").count()

    @property
    def get_confirmed_count(self):
        return Participation.objects.all().filter(
                challenge=self, status="2").count()

PARTICIPATION_STATE = enum(
    WAITING_FOR_CONFIRMATION = "0", 
    CONFIRMATION_DENIED ="1",
    CONFIRMED = "2",
    CANCELLED_BY_ADMIN = "3",
    CANCELLED_BY_USER = "4"
    )

participation_status_choices = [
    (PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION, _("Waiting for confirmation")),
    (PARTICIPATION_STATE.CONFIRMATION_DENIED, _("Confirmation denied")),
    (PARTICIPATION_STATE.CONFIRMED, _("Confirmed")),
    (PARTICIPATION_STATE.CANCELLED_BY_ADMIN, _("Cancelled by admin")),
    (PARTICIPATION_STATE.CANCELLED_BY_USER, _("Cancelled by user")),
    ]

class Participation(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"))
    challenge = models.ForeignKey(Challenge, verbose_name=_("Challenge"))

    application_text = models.TextField(
            null=True, blank=True, verbose_name=_("Application text"))
    cancellation_text = models.TextField(
            null=True, blank=True, verbose_name=_("Cancellation text"))
            
    status = models.CharField(
            max_length=2, choices=participation_status_choices, default="0",
            verbose_name=_("Status"))

    date_created = models.DateField(
            auto_now_add=True, verbose_name=_("Date created"))
    date_accepted = models.DateField(
            null=True, blank=True, verbose_name=_("Date accepted"))
    date_cancelled = models.DateField(
            null=True, blank=True, verbose_name=_("Date cancelled"))

    share_on_FB = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('participation')
        verbose_name_plural = _('participations')
        ordering = ['date_created',]
        
    def __unicode__(self):
        return unicode("%s - %s" % (self.user.username, self.challenge.name))

    @property
    def stat_participation_status_name(self):
        for code, name in participation_status_choices:
            if self.status == code:
                return name
        return ''

class Comment(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"))
    challenge = models.ForeignKey(Challenge, verbose_name=_("Challenge"))
    text = models.TextField(verbose_name=_("Text"))
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('commment')
        verbose_name_plural = _('comments')
        ordering = ['created_at',]
