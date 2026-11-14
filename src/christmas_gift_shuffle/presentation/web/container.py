import streamlit as st

from christmas_gift_shuffle.application.services import GiftExchangeService
from christmas_gift_shuffle.infrastructure.dependencies import create_repository


@st.cache_resource
def get_repository():
    return create_repository()


def get_service() -> GiftExchangeService:
    return GiftExchangeService(get_repository())