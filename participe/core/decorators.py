from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from participe.account.utils import is_challenge_admin
from participe.challenge.models import Challenge


# Prevents for all registered users (not only challenge admins)
# to challenge edit page via direct link
def challenge_admin(func):
    def _check(request, *args, **kwargs):
        challenge_id = kwargs.get("challenge_id", None)
        challenge = get_object_or_404(Challenge, pk=challenge_id)

        if is_challenge_admin(request.user, challenge):
            return func(request, *args, **kwargs)
        else:
            info = _("You don't have permission to perform this action.")
            return render_to_response('account_information.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
    return _check
