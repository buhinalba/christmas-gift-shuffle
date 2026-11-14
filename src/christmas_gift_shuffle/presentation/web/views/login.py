import streamlit as st


def render() -> None:
    st.title("Christmas Gift Shuffle")
    st.caption("A little Christmas magic.")
    st.button("Sign in with Google", type="primary", on_click=st.login)