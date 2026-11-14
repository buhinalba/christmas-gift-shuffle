import streamlit as st
from christmas_gift_shuffle.application.services import GiftExchangeService


def render_participant_page(service: GiftExchangeService, email: str) -> None:
    st.header("Your gift assignments")
    exchanges = service.list_for_participant(email)
    if not exchanges:
        st.info("No published exchanges are associated with this account.")
        return
    normalized = email.strip().casefold()
    for exchange in exchanges:
        participant = next((p for p in exchange.participants if p.email == normalized), None)
        if participant is None:
            continue
        st.subheader(exchange.name)
        people = {p.id: p.name for p in exchange.participants}
        themes = {t.id: t for t in exchange.themes}
        for assignment in exchange.assignments:
            if assignment.buyer_id != participant.id:
                continue
            theme = themes[assignment.theme_id]
            with st.container(border=True):
                st.markdown(f"**{theme.name}**")
                if theme.description:
                    st.caption(theme.description)
                st.write(f"Buy a gift for **{people[assignment.recipient_id]}**.")
