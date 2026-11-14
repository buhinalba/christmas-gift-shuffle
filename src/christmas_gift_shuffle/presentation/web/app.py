import streamlit as st

from christmas_gift_shuffle.presentation.web import auth
from christmas_gift_shuffle.presentation.web.views import admin, home, login


def main() -> None:
    st.set_page_config(page_title="Christmas Gift Shuffle", page_icon="🎁", layout="wide")

    if not auth.is_logged_in():
        st.navigation([st.Page(login.render, title="Sign in", url_path="login")]).run()
        return

    pages = [st.Page(home.render, title="My exchange", icon="🎁", url_path="home", default=True)]
    if auth.is_admin():
        pages.append(st.Page(admin.render, title="Admin", icon="🛠️", url_path="admin"))

    with st.sidebar:
        st.caption(f"Signed in as {auth.email()}")
        st.button("Log out", on_click=st.logout)

    st.navigation(pages).run()