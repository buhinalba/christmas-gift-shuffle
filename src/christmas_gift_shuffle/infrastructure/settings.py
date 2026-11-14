import streamlit as st


def admin_emails() -> set[str]:
    raw = st.secrets.get("app", {}).get("admin_emails", [])
    return {e.strip().lower() for e in raw}