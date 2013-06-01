from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from django_countries import CountryField
from easy_thumbnails.fields import ThumbnailerImageField


class Organization(models.Model):
    avatar = ThumbnailerImageField(
            upload_to='img/organizations', blank=True,
            verbose_name=_("Avatar"))
    name = models.CharField(max_length=80, verbose_name=_("Name"))
    description = models.TextField(
            null=True, blank=True, verbose_name=_("Description"))

    address_1 = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("Address 1"))
    address_2 = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("Address 2"))
    postal_code = models.PositiveIntegerField(
            null=True, blank=True, verbose_name=_("Postal Code"))
    city = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("City"))
    country = CountryField(
            verbose_name=_("Country"))
    
    website = models.URLField(null=True, blank=True, verbose_name=_("Website"))
    video = models.URLField(null=True, blank=True, verbose_name=_("Video"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("E-mail"))
    
    affiliated_users = models.ManyToManyField(
            User, null=True, blank=True, verbose_name=_("Affiliated Users"))
    
    is_contact_person = models.BooleanField(default=True)
    contact_person = models.ForeignKey(
            User, related_name="contact_org_set",
            verbose_name=_("Contact Person"))
    
    is_alt_person = models.BooleanField(default=False)
    alt_person_fullname = models.CharField(
            max_length=80, null=True, blank=True, verbose_name=_("Full Name"))
    alt_person_email = models.EmailField(
            max_length=80, null=True, blank=True, verbose_name=_("E-mail"))
    alt_person_phone = models.CharField(
            max_length=15, blank=True, default='',
            verbose_name=_("Phone Number"))

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        ordering = ['name',]

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('participe.organization.views.organization_detail',
                args=[str(self.id), slugify(self.name)])

    def get_hours_worked(self):
        from participe.challenge.models import Challenge, CHALLENGE_STATUS

        hours_worked = Challenge.objects.filter(
                status=CHALLENGE_STATUS.COMPLETED,
                organization=self,
                is_deleted=False).aggregate(Sum("duration"))
        return hours_worked["duration__sum"]

    def get_upcoming_challenges(self):
        from participe.challenge.models import Challenge, CHALLENGE_STATUS
        upcoming_challenges = Challenge.objects.filter(
                organization=self,
                status=CHALLENGE_STATUS.UPCOMING,
                is_deleted=False)

        return upcoming_challenges
