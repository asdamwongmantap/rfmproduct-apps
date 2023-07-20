import streamlit as st
import pandas as pd
import numpy as np

def app():
    st.markdown("---")
    st.title('Welcome To RFM-Product Dashboard')

    st.write(" RFM-Product Dashboard merupakan tampilan visual yang dapat digunakan untuk mempresentasikan informasi mengenai produk secara ringkas dan terstruktur. Dashboard ini dapat digunakan untuk memantau produk, menganalisis tren penjualan produk, dan dapat digunakan sebagai bahan untuk pengambilan keputusan .")
    
    st.write('Silahkan Upload File dan Pilih Menu Sidebar untuk mulai melakukan analisa')
    # st.write('')
    st.markdown("---")
