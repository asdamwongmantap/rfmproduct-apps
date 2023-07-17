import streamlit as st
# from multiapp import MultiApp
from apps import dashboard,analyze,cluster # import your app modules here
import pandas as pd
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth

def mainmenu():
    st.set_page_config(page_title="RFMProduct-Apps", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

    with st.sidebar:
        selected = option_menu("Main Menu", ["Dashboard","Analisa Produk", 'Klaster Produk'], 
            icons=['house','basket', 'pie-chart'], menu_icon="cast", default_index=0)
        selected

    if selected == 'Dashboard':
        dashboard.app()
    elif selected == 'Analisa Produk':
        analyze.app()
    elif selected == 'Klaster Produk':
        rfm = analyze.app()
        cluster.app(rfm)