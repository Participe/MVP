from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from django_countries import CountryField


class Organization(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField(null=True, blank=True)

    address_1 = models.CharField(max_length=80, null=True, blank=True)
    address_2 = models.CharField(max_length=80, null=True, blank=True)
    postal_code = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=80, null=True, blank=True)
    country = CountryField()
    
    website = models.URLField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    is_contact_person = models.BooleanField(default=True)
    contact_person = models.ForeignKey(User)
    
    is_alt_person = models.BooleanField(default=False)
    alt_person_fullname = models.CharField(max_length=80, null=True, blank=True)
    alt_person_email = models.EmailField(max_length=80, null=True, blank=True)
    alt_person_phone = models.CharField(max_length=15, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'organization'
        verbose_name_plural = 'organizations'
        ordering = ['name',]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('participe.organization.views.organization_detail', args=[str(self.id)])
