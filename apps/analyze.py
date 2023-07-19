import streamlit as st
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
import numpy as np
from decimal import *
import re
# from datetime import datetime
from dateutil import parser
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import datetime
import calendar
import matplotlib.pyplot as plt


def app():
    dateAnalyze = st.date_input("Tanggal Analisa", datetime.date(2023, 7, 3))
    st.write("Untuk Melakukan Analisa Produk, Pengguna Perlu melakukan upload data csv yang didapat dari datawarehouse terlebih dahulu")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # ubah file csv menjadi dataframe
        data = loadCsv(uploaded_file)

        # tampilkan 3 baris pertama
        rfm = rfmAll(data,dateAnalyze)
        option = st.selectbox(
            'Silahkan pilih tampilan informasi yang ingin ditampilkan!',
            ('-', 'Text', 'Visual'))

        if option == 'Text':
            infoByText(data,rfm)
        elif option == 'Visual':
            infoByChart(data,rfm)

        
        return rfm

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

def masking(data):
    dfDropCol = data
    curr_obj = None
    for i, dfMarkUp in enumerate(dfDropCol['Price']):
        subTotalMarkup = dfDropCol.loc[dfDropCol.index[i], 'Subtotal'] + 123456
        totalMarkup =  dfDropCol.loc[dfDropCol.index[i], 'Total'] + 123456
        #markup price product
        obj = dfDropCol['Price'][i]
        # dfDropCol['Price'][i] = dfDropCol['Price'][i] + 400500 + i
        dfDropCol.loc[dfDropCol.index[i], 'Price'] = dfDropCol.loc[dfDropCol.index[i], 'Price'] + 123456
        # dfDropCol['Subtotal'][i] = dfDropCol['Subtotal'][i] + 123456
        dfDropCol.loc[dfDropCol.index[i], 'Subtotal'] = subTotalMarkup
        # dfDropCol['Total'][i] = dfDropCol['Subtotal'][i] - dfDropCol['Potongan'][i]
        dfDropCol.loc[dfDropCol.index[i], 'Total'] = dfDropCol.loc[dfDropCol.index[i], 'Subtotal'] - dfDropCol.loc[dfDropCol.index[i], 'Potongan']
        # dfDropCol['Subtotal PerProduct'][i] = dfDropCol['Price'][i] * dfDropCol['Qty'][i]
        # dfDropCol.loc[dfDropCol.index[i], 'Subtotal PerProduct'] = dfDropCol.loc[dfDropCol.index[i], 'Price'] * dfDropCol.loc[dfDropCol.index[i], 'Qty']

    for i, dfOrder in enumerate(dfDropCol['Order ID']):
        #mask email cust
        findAt = str(dfDropCol['Email'][i]).find('@')
        if findAt > 0:
            dfDropCol['Email'][i] = dfDropCol['Email'][i][0]+"xxxx"+dfDropCol['Email'][i][findAt-1:]


        # dfDropCol['Subtotal'] = dfDropCol.groupby(['Order ID'])['Price'].agg('sum')
        #fill nan with value before
        # dfDropCol.fillna(method='ffill', inplace=True)
        # dfDropCol['Email'].fillna(value='-',inplace=True)
        dfDropCol['Supplier Price'].fillna(value=dfDropCol['Price']-600000,inplace=True)
        dfDropCol.fillna({'Email':'-','SKU':'-'},inplace=True)
        # dfDropCol['Supplier Price'].apply(lambda x: x.fillna(value=dfDropCol['Price']-600000))

    for i, dfMarkUpSub in enumerate(dfDropCol['Subtotal']):
        #markup price product
        next_obj = dfDropCol['Order ID'][i]
        if next_obj == curr_obj:
            dfDropCol.loc[dfDropCol.index[i], 'Subtotal'] = subTotalMarkup
            dfDropCol.loc[dfDropCol.index[i-1], 'Subtotal'] = dfDropCol.loc[dfDropCol.index[i], 'Subtotal']
            dfDropCol.loc[dfDropCol.index[i], 'Total'] = (totalMarkup) - dfDropCol.loc[dfDropCol.index[i], 'Potongan']
            dfDropCol.loc[dfDropCol.index[i-1], 'Total'] = dfDropCol.loc[dfDropCol.index[i], 'Total']
        curr_obj = next_obj
    return dfDropCol

def getTotalOrder(data):
    # dfDropCol.value_counts('SKU')
    sumValCounts = data.value_counts('SKU').sum()
    sumValCountsByOrder = data.value_counts('Order ID').sum()
    dfFrequentItem = data.value_counts('SKU',sort=True,ascending=False).reset_index(name='counts')
    dfFrequentItemByOrder = data.value_counts('Order ID',sort=True,ascending=False).reset_index(name='countsORDER')
    dfFrequentItem['MinSupport'] = 0
    for j, dfFrequentItemSupp in enumerate(dfFrequentItem['SKU']):
        dfFrequentItem.loc[dfFrequentItem.index[j], 'MinSupport'] =  dfFrequentItem.loc[dfFrequentItem.index[j], 'counts'] / sumValCounts
    # dfFrequentItem
    sumValCountsFI3 = len(dfFrequentItemByOrder)
    return sumValCountsFI3

def getMinSupport(data,totalOrder):
    datasetItemdrop = data.drop_duplicates(["Order ID", "SKU"])
    datasetItem = datasetItemdrop.groupby(['Order ID'], as_index=False)['SKU'].apply(', '.join)
    # min_suport all
    dfFrequentFI = datasetItem.value_counts('SKU',sort=True,ascending=False).reset_index(name='counts')
    dfFrequentFI['MinSupport'] = 0
    dfFrequentFI['MinSupportFloat'] = 0
    dfFrequentFI['CountItem'] = 0
    # dfFrequentFI.astype({'MinSupport':'float64','counts':'float64'})
    for j, dfFrequentItemSupp in enumerate(dfFrequentFI['SKU']):
        dfFrequentFI.loc[dfFrequentFI.index[j], 'MinSupport'] = "{:.6f}".format(dfFrequentFI.loc[dfFrequentFI.index[j], 'counts'] / np.int64(totalOrder))

    dfFrequentFI.loc[dfFrequentFI.index[j], 'MinSupport'] = re.findall(r'\d+\.\d+', dfFrequentFI.loc[dfFrequentFI.index[j], 'MinSupport'])[0]
    dfFrequentFI.loc[dfFrequentFI.index[j], 'MinSupportFloat'] = Decimal(dfFrequentFI.loc[dfFrequentFI.index[j], 'MinSupport'])
    dfFrequentFI.loc[dfFrequentFI.index[j], 'CountItem'] = len(dfFrequentFI.loc[dfFrequentFI.index[j], 'SKU'].split(','))
    # dfFrequentFI.astype({'MinSupport':'decimal'})
    return dfFrequentFI

def rfm1Item(data):
    dfFi1 = data.loc[(data['CountItem'] == 1) & (data['MinSupportFloat'] >= 0.0009)]
    return dfFi1

def rfm2Item(data):
    dfFi2 = data.loc[(data['CountItem'] == 2) & (data['MinSupportFloat'] >= 0.00001)]
    return dfFi2

def rfm2Item(data):
    dfFi2 = data.loc[(data['CountItem'] == 2) & (data['MinSupportFloat'] >= 0.00001)]
    return dfFi2

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
def loadCsv(url):
    df = pd.read_csv(url)
    data = deleteUnusedColumn(df)
    data = renameColumn(data)
    return data

@st.cache_data
def loadTotalOrder(data):
    return getTotalOrder(data)

def infoByText(data,rfm):
    category = st.radio(
            "Informasi Yang Diinginkan",
            ('Total Order','Produk Yang Belum Lama Terjual',
             'Produk Yang Banyak Terjual','Produk Yang Banyak Memberikan Keuntungan'))
    if category == 'Total Order':
        totalOrder = loadTotalOrder(data)
        st.write('Total Order Keseluruhan Sebanyak ',totalOrder)
    elif category == 'Produk Yang Belum Lama Terjual':
        st.write('Total Produk Yang Belum Lama Terjual Sebanyak ',len(rfm[rfm['Recency'] == rfm['Recency'].min()]))
        st.write(rfm[rfm['Recency'] == rfm['Recency'].min()])
    elif category == 'Produk Yang Banyak Terjual':
        st.write('Total Produk Yang Banyak Terjual Sebanyak ',len(rfm[rfm['Frequency'] == rfm['Frequency'].max()]))
        st.write(rfm[rfm['Frequency'] == rfm['Frequency'].max()])
    elif category == 'Produk Yang Banyak Memberikan Keuntungan':
        st.write('Total Produk Yang Banyak Memberikan Keuntungan Sebanyak ',len(rfm[rfm['Monetary'] == rfm['Monetary'].max()]))
        st.write(rfm[rfm['Monetary'] == rfm['Monetary'].max()])

    return rfm

def infoByChart(data,rfm):
    rfm['Month'] = pd.DatetimeIndex(rfm['Last Order Date']).month
    rfm['Year'] = pd.DatetimeIndex(rfm['Last Order Date']).year
    rfm['MonthStr'] = rfm['Month'].apply(lambda x: calendar.month_abbr[x])
    rfm['Year'] = rfm['Year'].astype(str)
    rfm['YearShort'] = rfm['Year'].apply(lambda x: x[-2:])
    rfm['MonthYearStr'] = rfm['MonthStr']+rfm['YearShort']
    rfm['MonthYearSort'] = rfm['YearShort']+"-"+rfm['Month'].astype(str)


    left_col, mid_col, right_col = st.columns(3)
    with left_col:
        st.write("Total Order:")
        st.write(f"{loadTotalOrder(data)}")
    with mid_col:
        st.write("Total Produk:")
        st.write(f"{len(rfm)}")
    with right_col:
        st.write("Profit Produk Tertinggi:")
        st.write(rfm[rfm['Monetary'] == rfm['Monetary'].max()]['Monetary'])

    st.markdown("---")

    left_colchart, mid_colchart, right_colchart = st.columns(3)
    with left_colchart:
        st.write("Produk Berdasarkan Rentang Waktu (Recency):")
        # group data for chart
        monthYearSortDF = rfm.value_counts('MonthYearSort').reset_index(name='countsMonthYearSort').sort_values(by='MonthYearSort')
        monthYearSortDF['MonthSplit'] = 0
        for j, dfMonthYear in enumerate(monthYearSortDF['MonthYearSort']):
            monthYearSortDF.loc[monthYearSortDF.index[j], 'MonthYearSplit'] = monthYearSortDF.loc[monthYearSortDF.index[j], 'MonthYearSort'].split("-")[0]
            monthYearSortDF.loc[monthYearSortDF.index[j], 'MonthSplit'] =  int(monthYearSortDF.loc[monthYearSortDF.index[j], 'MonthYearSort'].split("-")[1])

        monthYearSortDF['MonthStr'] = monthYearSortDF['MonthSplit'].apply(lambda x: calendar.month_name[x])
        monthYearSortDF['MonthYearStr'] = monthYearSortDF['MonthStr']+" "+monthYearSortDF['MonthYearSplit']

        # create chart
        fig, ax = plt.subplots()
        savefig = plt.savefig('product_recency.png')
        ax.plot(monthYearSortDF['MonthYearStr'],monthYearSortDF['countsMonthYearSort'])
        ax.tick_params(axis='x', rotation=70)
        st.pyplot(savefig)

    with mid_colchart:
        st.write("Produk Berdasarkan Jumlah pembelian (Frequency):")
        # group data for chart
        for k, dfFrequency in enumerate(rfm['Frequency']):
            if rfm.loc[rfm.index[k], 'Frequency'] <= 6:
                rfm.loc[rfm.index[k], 'FrequencyClass'] = "0 - 6"
            elif rfm.loc[rfm.index[k], 'Frequency'] > 6 and rfm.loc[rfm.index[k], 'Frequency'] <= 50:
                rfm.loc[rfm.index[k], 'FrequencyClass'] = "7 - 50"
            elif rfm.loc[rfm.index[k], 'Frequency'] > 50:
                rfm.loc[rfm.index[k], 'FrequencyClass'] = "> 50"

        frequentcountDF = rfm.value_counts('FrequencyClass').reset_index(name='countsFrequencyClass')

        # create chart
        fig, ax = plt.subplots()
        savefig = plt.savefig('product_frequency.png')
        ax.pie(frequentcountDF['countsFrequencyClass'], labels=frequentcountDF['FrequencyClass'])
        st.pyplot(savefig)

    with right_colchart:
        st.write("Produk Berdasarkan Keuntungan / Profit (Monetary):")
        # group data for chart
        for k, dfMonetary in enumerate(rfm['Monetary']):
            if rfm.loc[rfm.index[k], 'Monetary'] <= 500000:
                rfm.loc[rfm.index[k], 'MonetaryClass'] = "1 - 500.000"
            elif rfm.loc[rfm.index[k], 'Monetary'] > 500000 and rfm.loc[rfm.index[k], 'Monetary'] <= 5000000:
                rfm.loc[rfm.index[k], 'MonetaryClass'] = "501.000 - 5.000.000"
            elif rfm.loc[rfm.index[k], 'Monetary'] > 5000000:
                rfm.loc[rfm.index[k], 'MonetaryClass'] = "> 5.000.000"

        monetarycountDF = rfm.value_counts('MonetaryClass').reset_index(name='countsMonetaryClass').sort_values('MonetaryClass')

        # create chart
        fig, ax = plt.subplots()
        savefig = plt.savefig('product_recency.png')
        ax.bar(monetarycountDF['MonetaryClass'],monetarycountDF['countsMonetaryClass'])
        ax.tick_params(axis='x', rotation=70)
        st.pyplot(savefig)

    return rfm

    