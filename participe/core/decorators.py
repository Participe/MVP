from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from participe.account.utils import is_challenge_admin
from participe.challenge.models import Challenge, Participation, Comment


# Prevents for all registered users (not only challenge admins)
# to challenge edit page via direct link
def challenge_admin(func):
    def _check(request, *args, **kwargs):
        is_authorized_action = False

        challenge_id = kwargs.get("challenge_id", None)
        if challenge_id:
            challenge = get_object_or_404(Challenge, pk=challenge_id)

        participation_id = kwargs.get("participation_id", None)
        if participation_id:
            participation = get_object_or_404(
                    Participation, pk=participation_id)
            challenge = participation.challenge

        comment_id = kwargs.get("comment_id", None)
        if comment_id:
            comment = get_object_or_404(Comment, pk=comment_id)
            challenge = comment.challenge
            if request.user==comment.user:
                is_authorized_action = True

        if is_challenge_admin(request.user, challenge) or is_authorized_action:
            return func(request, *args, **kwargs)
        else:
            info = _("You don't have permission to perform this action.")
            return render_to_response('account_information.html', 
                    RequestContext(request, {
                            "information": info,
                            }))
    return _check
