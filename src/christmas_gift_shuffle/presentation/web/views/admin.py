import streamlit as st

from christmas_gift_shuffle.application.services import AssignmentService
from christmas_gift_shuffle.domain.entities import Participant, Theme
from christmas_gift_shuffle.domain.strategies import CyclicAssignmentStrategy
from christmas_gift_shuffle.presentation.web import auth
from christmas_gift_shuffle.presentation.web.container import get_repository, get_service
from christmas_gift_shuffle.presentation.web.views.participant import render_participant_page


def _lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _parse_participants(text: str) -> list[Participant]:
    people, seen = [], set()
    for n, line in enumerate(_lines(text), start=1):
        parts = [p.strip() for p in line.split(",", 1)]
        if len(parts) != 2 or not parts[0] or "@" not in parts[1]:
            raise ValueError(f"Participant line {n} must be: Name, email")
        email = parts[1].lower()
        if email in seen:
            raise ValueError(f"Duplicate email on line {n}: {email}")
        seen.add(email)
        people.append(Participant(parts[0], email))
    return people


def render() -> None:
    auth.require_admin()
    service, repository = get_service(), get_repository()

    st.title("Organiser")

    if msg := st.session_state.pop("flash", None):
        st.success(msg)

    with st.form("create_exchange"):
        name = st.text_input("Exchange name", placeholder="Family Christmas 2026")
        c1, c2 = st.columns(2)
        people_text = c1.text_area("Participants (Name, Gmail per line)", height=220,
                                   placeholder="Alex, alex@gmail.com")
        themes_text = c2.text_area("Themes (one per line)", height=220)
        submitted = st.form_submit_button("Create draft exchange", type="primary")

    if submitted:
        try:
            people = _parse_participants(people_text)
            exchange = service.create_draft(name, people, [Theme(t) for t in _lines(themes_text)])
            st.session_state["flash"] = f"Created draft: {exchange.name}"
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    exchanges = service.list_all()
    if not exchanges:
        st.info("No exchanges yet.")
        return

    st.divider()
    choices = {f"{e.name} | {e.status.value} | {e.id[:8]}": e.id for e in exchanges}
    exchange = service.get(choices[st.selectbox("Select exchange", list(choices))])

    st.write(f"**{len(exchange.participants)} participants, {len(exchange.themes)} themes**")



    if exchange.status.value == "draft":

        # edit exchange details
        with st.expander("Edit draft"):
            with st.form(f"edit_{exchange.id}"):
                new_name = st.text_input("Exchange name", value=exchange.name)
                c1, c2 = st.columns(2)
                new_people = c1.text_area(
                    "Participants (Name, Gmail per line)", height=220,
                    value="\n".join(f"{p.name}, {p.email}" for p in exchange.participants))
                new_themes = c2.text_area(
                    "Themes (one per line)", height=220,
                    value="\n".join(t.name for t in exchange.themes))
                saved = st.form_submit_button("Save changes", type="primary")
            if saved:
                try:
                    service.update_draft(
                        exchange.id, new_name, _parse_participants(new_people),
                        [Theme(t) for t in _lines(new_themes)])
                    st.session_state["flash"] = "Draft updated."
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        # Generate and Lock
        if st.button("Generate and lock assignments", type="primary"):
            try:
                generated = AssignmentService(CyclicAssignmentStrategy()).generate(exchange)
                repository.save_generated_exchange(generated)
                st.session_state["flash"] = "Assignments generated and locked."
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        with st.expander("Delete draft"):
            st.warning("This permanently deletes the draft with its participants and themes.")
            confirm = st.checkbox(
                f"Yes, delete \"{exchange.name}\"",
                key=f"confirm_delete_{exchange.id}",
            )
            if st.button("Delete draft", type="primary", disabled=not confirm,
                         key=f"delete_{exchange.id}"):
                try:
                    service.delete_draft(exchange.id)
                    st.session_state["flash"] = f"Deleted draft: {exchange.name}"
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    else:
        names = {p.id: p.name for p in exchange.participants}
        themes = {t.id: t.name for t in exchange.themes}
        with st.expander("Full allocation (organiser only)"):
            st.dataframe(
                [{"Buyer": names[a.buyer_id], "Recipient": names[a.recipient_id],
                  "Theme": themes[a.theme_id]} for a in exchange.assignments],
                hide_index=True,
            )
        with st.expander("Preview as participant"):
            emails = [p.email for p in exchange.participants]
            who = st.selectbox("View as", emails)
            render_participant_page(service, who)

