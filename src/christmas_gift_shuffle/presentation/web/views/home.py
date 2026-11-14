from christmas_gift_shuffle.presentation.web import auth
from christmas_gift_shuffle.presentation.web.container import get_service
from christmas_gift_shuffle.presentation.web.views.participant import render_participant_page


def render() -> None:
    render_participant_page(get_service(), auth.email())