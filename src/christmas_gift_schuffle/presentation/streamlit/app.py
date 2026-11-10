import streamlit as st
from ...application.services import GiftExchangeService
from ...infrastructure.dependencies import create_repository
from .pages.admin import render_admin_page
from .pages.participant import render_participant_page

st.set_page_config(page_title="Christmas Gift Schuffle", page_icon="🎁", layout="wide")
st.title("Christmas Gift Schuffle")
st.caption("A little Christmas magic.")


print("MAIN APP LOADED")

@st.cache_resource
def get_repository():
    return create_repository()

repository = get_repository()
service = GiftExchangeService(repository)
mode = st.sidebar.radio("Development view", ["Organiser preview", "Participant preview"])
if mode == "Organiser preview":
    st.warning("Development-only preview. Organiser access is not protected yet; do not deploy publicly.")
    render_admin_page(service, repository)
else:
    st.warning("Development-only email selector, NOT authentication. Google OAuth is a later phase.")
    email = st.text_input("Preview participant email")
    if email:
        render_participant_page(service, email)
