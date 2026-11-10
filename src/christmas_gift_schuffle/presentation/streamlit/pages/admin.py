import streamlit as st
from ....application.services import AssignmentService, GiftExchangeService
from ....domain.entities import Participant, Theme
from ....domain.strategies import CyclicAssignmentStrategy


def _lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def render_admin_page(service: GiftExchangeService, repository) -> None:
    print("ADMIN PAGE RENDERED")
    st.header("Organiser")
    st.caption("Create an exchange, register participants and themes, then generate the draw.")
    with st.form("create_exchange"):
        name = st.text_input("Exchange name", placeholder="Family Christmas 2026")
        col1, col2 = st.columns(2)
        with col1:
            people_text = st.text_area("Participants — one per line: Name, Gmail", height=220,
                placeholder="Alex, alex@gmail.com\nSam, sam@gmail.com")
        with col2:
            themes_text = st.text_area("Themes — one per line", height=220,
                placeholder="Childhood nostalgia\nBeautifully useless")
        submitted = st.form_submit_button("Create draft exchange", type="primary")
        st.write("Submitted:", submitted)

    if submitted:
        try:
            print("Create Draft submitted")
            st.write("Form submitted!")
            people = []
            for number, line in enumerate(_lines(people_text), start=1):
                parts = [part.strip() for part in line.split(",", 1)]
                if len(parts) != 2:
                    raise ValueError(f"Participant line {number} must be: Name, email")
                people.append(Participant(parts[0], parts[1]))
            themes = [Theme(theme) for theme in _lines(themes_text)]
            exchange = service.create_draft(name, people, themes)
            st.success(f"Created draft: {exchange.name}")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    exchanges = service.list_all()
    if not exchanges:
        st.info("No exchanges yet.")
        return
    st.divider()
    st.subheader("Existing exchanges")
    choices = {f"{e.name} · {e.status.value} · {e.id[:8]}": e.id for e in exchanges}
    label = st.selectbox("Select exchange", list(choices))
    exchange = service.get(choices[label])
    st.write(f"**{len(exchange.participants)} participants · {len(exchange.themes)} themes**")
    with st.expander("Review participants and themes"):
        st.dataframe([{"Name": p.name, "Google email": p.email} for p in exchange.participants], hide_index=True)
        st.write([t.name for t in exchange.themes])

    if exchange.status.value == "draft":
        if st.button("Generate and lock assignments", type="primary"):
            try:
                generated = AssignmentService(CyclicAssignmentStrategy()).generate(exchange)
                repository.save_generated_exchange(generated)
                st.success("Assignments generated and locked.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    else:
        st.success("Assignments are generated and locked.")
        with st.expander("View complete allocation — organiser only"):
            names = {p.id: p.name for p in exchange.participants}
            theme_names = {t.id: t.name for t in exchange.themes}
            st.dataframe([{"Buyer": names[a.buyer_id], "Recipient": names[a.recipient_id],
                           "Theme": theme_names[a.theme_id]} for a in exchange.assignments], hide_index=True)
