import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from apps import dashboard,analyze,cluster # import your app modules here
import pandas as pd
from streamlit_option_menu import option_menu
import datetime

st.set_page_config(page_title="RFMProduct-Apps", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

def deleteUnusedColumn(df):
    dfDropCol = df.drop(['Fulfillment Item ID',
        'Fulfillment ID',
        'Fulfillment Code',
        'Fulfillment Name',
        'Fulfillment Note',
        'Order ID',
        'Order Source',
        'Order Source Code',
        'Order Reference',
        'Order Source Category',
        'Order Tags',
        'Order Office ID',
        'Order Office Name',
        'Order Courier ID',
        'Payment ID',
        'Customer ID',
        'Order Office Type',
        'Customer Name',
        'Customer Phone',
        'Order External ID',
        'Payment Gateway Names',
        'Order Status ID',
        'Order Status',
        'Order Payment Status ID',
        'Payment Names',
        'Payment Status',
        'Order Integration Status ID',
        'Order Integration Status',
        'Order Item ID',
        'Order Product ID',
        'Order Variant ID',
        'Order At Jkt',
        'Order Created At',
        'Month Bucket Jkt',
        'Order Updated At',
        'Order Process At',
        'Order Updated At Jkt',
        'Order Process At Jkt',
        'Reseller Selling Price',
        'Month Bucket Process Jkt',
        'Product ID',
        'Variant ID',
        'Category Name',
        'Subcategory Name',
        'Subcategory Code',
        'Item Code',
        'Sku Universal',
        'Product Gender',
        'Brand Code',
        'Brand Name',
        'Purchasing Src',
        'Product Tags',
        'Receiver Phone',
        'Receiver Address',
        'Receiver City',
        'Receiver Zipcode',
        'Province ID',
        'Province Name',
        'Brand Category',
        'District ID',
        'District Name',
        'Subdistrict ID',
        'Fulfillment Office Type',
        'Subdistrict Name',
        'Receipt No',
        'Fulfillment Office ID',
        'Fulfillment Office Name',
        'Fulfillment Courier ID',
        'Latitude',
        'Longitude',
        'Transfer Unique Code',
        'Fulfillment Status ID',
        'Fulfillment Status',
        'Marketplace Owned By Mw',
        'Dropship Name',
        'Dropship Note',
        'Fulfillment External ID',
        'Booking Code',
        'Shipping Note',
        'Dropship Phone',
        'Marketplace Code',
        'Marketplace Phone',
        'Marketplace Store',
        'Picker',
        'Start Picking At Jkt',
        'End Picking At Jkt',
        'Start Picking At',
        'End Picking At',
        'Packer',
        'Start Packing At',
        'End Packing At',
        'Start Packing At Jkt',
        'End Packing At Jkt',
        'Order Cancel Reason',
        'Is Return',
        'Is Consign',
        'Is Reseller',
        'Is International',
        'Is Order Deleted',
        'Is Fulfillment Deleted',
        'Is Fulfillment Item Deleted',
        'Fulfillment Created By',
        'Fulfillment Created At',
        'Fulfillment Updated By',
        'Fulfillment Created At Jkt',
        'Fulfillment Updated At',
        'Fulfillment Updated At Jkt',
        'Is Product Consign',
        'Is Hermes Kbc',
        'Prorate Day Of Month',
        'Monthly Ordet Net Price',
        'Monthly Supplier Price',
        'Stdcost Freight Out Conf',
        'Shipment At',
        'Stdcost Freight Out Val',
        'Shipment At Jkt',
        'Stdcost Freight In Percentage',
        'Stdcost Freight In Percentage Calc',
        'Stdcost Freight In Fixed',
        'Stdcost Freight In Val',
        'Stdcost Packaging Conf',
        'Stdcost Packaging Val',
        'Stdcost Prepaid Rental Conf',
        'Stdcost Prepaid Rental Val',
        'Stdcost Shopify Conf',
        'Stdcost Shopify Val',
        'Stdcost Midtrans Conf',
        'Stdcost Midtrans Val',
        'Stdcost Maintenance Conf',
        'Stdcost Maintenance Val',
        'Stdcost Forex Conf',
        'Stdcost Forex Val',
        'Stdcost Interest Conf',
        'Stdcost Interest Val',
        'Stdcost Marketplace Conf',
        'Stdcost Marketplace Val',
        'Stdcost Total','Prorate Total Discount','Receiver Email','Order At','Receiver Email'], axis=1)

    dfDropCol['Qty'] = 1
    dfDropCol['Price'] = dfDropCol['Order Price']

    return dfDropCol

def renameColumn(data):
    data.rename(columns = {'Order Number':'Order ID',
                            'Sku Barcode':'SKU',
                            'Order Price':'Subtotal','Prorate Actual Discount':'Potongan','Order Net Price':'Total',
                            'Order Created At Jkt':'Order Date',
                            'Customer Email':'Email'	}, inplace = True)

    data = data
    return data

def rfmAll(data,snapShotDate):
    data['Order Date'].fillna('-')
    data['dateSplit'] = ""
    data['todaySplit'] = ""
    data['profit'] = 0
    # now = datetime.now()
    # today = now.strftime("%Y-%m-%d")
    for l, dfFrequentItemSuppDate in enumerate(data['Order Date']):
        splitDate = data.loc[data.index[l], 'Order Date'].split("T")[0]
        if len(splitDate) > 0:
            data.loc[data.index[l], 'dateSplit'] = splitDate

            data.loc[data.index[l], 'todaySplit'] = snapShotDate

            data.loc[data.index[l], 'profit'] = data.loc[data.index[l], 'Subtotal'] - data.loc[data.index[l], 'Supplier Price']

    dfDropCol2 = data
    data["todaySplit"] = pd.to_datetime(data["todaySplit"]) # excluding hours and minutes.
    data["dateSplit"] = pd.to_datetime(data["dateSplit"]) # excluding hours and minutes.
    snapshot = data["todaySplit"].max() # the last day is our max date
    # snapshot = '2023-07-03'
    sku_group = data.groupby("SKU") # grouping the sku id's to see every single sku's activity on r, f , m
    recency = (snapshot - sku_group["dateSplit"].max()) # the last day of grouped sku's transaction is captured with .max()
    frequency = sku_group["Order ID"].nunique() # how many times the sku made transactions?
    monetary = sku_group["profit"].sum()
    tenure = snapshot - sku_group["dateSplit"].min()  # the first day of grouped customer's transaction is captured with .min()
    rfm = pd.DataFrame() # opened a new rfm dataframe
    rfm["Recency"] = recency.dt.days # FORMAT CHANGE: timedelta64 to integer
    rfm["Frequency"] = frequency
    rfm["Monetary"] = monetary
    # rfm["Tenure"] = tenure.dt.days # FORMAT CHANGE: timedelta64 to integer
    rfm['Last Order Date'] = sku_group["dateSplit"].max()
    rfm['First Order Date'] = sku_group["dateSplit"].min()
    # rfm.reset_index(inplace=True)
    return rfm

@st.cache_data
def loadCsv(url,dateAnalyze):
    df = pd.read_csv(url)
    data = deleteUnusedColumn(df)
    data = renameColumn(data)

    rfm = rfmAll(data,dateAnalyze)
    return data,rfm


name, authentication_status, username = authenticator.login("Login", "main")
if authentication_status:
    authenticator.logout('Logout', 'main')

    dateAnalyze = st.date_input("Tanggal Analisa", datetime.date(2023, 7, 3))

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # ubah file csv menjadi dataframe
        data,rfm = loadCsv(uploaded_file,dateAnalyze)
    
    with st.sidebar:
        selected = option_menu("Main Menu", ["Dashboard","Analisa Produk", 'Klaster Produk'], 
            icons=['house','basket', 'pie-chart'], menu_icon="cast", default_index=0)
        selected

    if selected == 'Dashboard':
        dashboard.app()
    elif selected == 'Analisa Produk':
        analyze.app()
    elif selected == 'Klaster Produk':
        # rfm = analyze.app()
        cluster.app(rfm)
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

