import streamlit as st

from christmas_gift_shuffle.infrastructure.settings import admin_emails


def is_logged_in() -> bool:
    return bool(st.user.is_logged_in)


def email() -> str:
    return (st.user.get("email") or "").strip().lower()


def is_admin() -> bool:
    # Google sets email_verified; don't trust unverified emails for admin rights
    return (
        is_logged_in()
        and bool(st.user.get("email_verified", True))
        and email() in admin_emails()
    )


def require_admin() -> None:
    if not is_admin():
        st.error("You don't have access to this page.")
        st.stop()