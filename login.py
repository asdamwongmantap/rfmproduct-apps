import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['abc', 'def']).generate()

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login("Login", "sidebar")
st.write(authentication_status)
st.write(config['credentials'])
if authentication_status:
    authenticator.logout('Logout', 'main')
    if username == 'operation':
        st.write(f'Welcome *{name}*')
        st.title('Application 1')
    elif username == 'finance':
        st.write(f'Welcome *{name}*')
        st.title('Application 2')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')