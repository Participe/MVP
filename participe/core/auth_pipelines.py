import json
import urllib

from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from participe.account.models import UserProfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


def get_user_avatar(backend, details, response, social_user, uid, user, \
        *args, **kwargs):
    try:
        profile = get_object_or_404(UserProfile, user=user)
    except:
        profile = UserProfile.objects.create(user=user)

    try:
        url = ("http://graph.facebook.com/%s/picture?type=large"
                % response['id'])
        if url:
            fb_avatar = urllib.urlopen(url).read()
            image = Image.open(StringIO(fb_avatar))

            thumb = StringIO()
            image.save(
                    thumb, settings.AVATAR_THUMB_FORMAT,
                    quality=settings.AVATAR_THUMB_QUALITY)
            thumb_file = ContentFile(thumb.getvalue())

            profile.avatar.save("%s_facebook%s" % (uid, ".jpg"), thumb_file)
            profile.save()
    except:
        # Unexpected error. Just pass by.
        pass

def get_extra_data(backend, details, response, social_user, uid, user, \
        *args, **kwargs):
    from django_countries.countries import COUNTRIES
    
    try:
        profile = get_object_or_404(UserProfile, user=user)
    except:
        profile = UserProfile.objects.create(user=user)

    try:
        access_token = social_user.extra_data["access_token"]
        fb_profile = urllib.urlopen(
                'https://graph.facebook.com/me?access_token=%s' % access_token)
        fb_profile = json.load(fb_profile)
        
        birthday = fb_profile.get("birthday", "")
        if birthday:
            profile.birth_day = datetime.strptime(birthday, "%m/%d/%Y"
                    ).strftime("%d.%m.%Y")

        location = fb_profile.get("location", "").get("name", "")
        city, country = location.split(", ")
        if city:
            profile.city = city
        if country:
            for code, name in COUNTRIES:
                if name.lower()==country.lower():
                    profile.country = code

        profile.save()
    except:
        # Unexpected error. Just pass by.
        pass
