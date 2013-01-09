from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
import urllib
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
        # Avatar cannot be attached, unless user filled up all profile's
        # mandatory fields
        pass
