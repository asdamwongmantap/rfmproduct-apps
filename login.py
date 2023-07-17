import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from apps import dashboard,analyze,cluster # import your app modules here
import pandas as pd
from streamlit_option_menu import option_menu

hashed_passwords = stauth.Hasher(['abc', 'def']).generate()

st.set_page_config(page_title="RFMProduct-Apps", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login("Login", "main")
if authentication_status:
    authenticator.logout('Logout', 'main')
    
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
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')