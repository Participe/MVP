from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from participe.account.utils import get_admin_challenges
from participe.challenge.models import Challenge


# Prevents for all registered users (not only challenge admins)
# to challenge edit page via direct link
def challenge_admin(func):
    def _check(request, *args, **kwargs):
        challenge_id = kwargs.get("challenge_id", None)
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        admin_challenges = get_admin_challenges(request.user)

        if challenge in admin_challenges:
            return func(request, *args, **kwargs)
        else:
            info = _("You don't have permissions to perform this operation.")
            return render_to_response('account_information.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
    return _check
