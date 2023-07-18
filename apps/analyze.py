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



def app():
    dateAnalyze = st.date_input("Tanggal Analisa", datetime.date(2019, 7, 6))
    st.write("Untuk Melakukan Analisa Produk, Pengguna Perlu melakukan upload data csv yang didapat dari datawarehouse terlebih dahulu")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # ubah file csv menjadi dataframe
        df = pd.read_csv(uploaded_file)

        # tampilkan 3 baris pertama
        # st.write(df)


        data = deleteUnusedColumn(df)
        data = renameColumn(data)
        # data = masking(data)
        # totalOrder = getTotalOrder(data)
        # data = getMinSupport(data,totalOrder)
        # data = rfm1Item(data)
        rfm = rfmAll(data,dateAnalyze)
        gd = GridOptionsBuilder.from_dataframe(rfm)
        gd.configure_pagination(enabled=True,paginationPageSize=10)
        # gd.configure_side_bar()
        gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True,filterable=True)
        gridOptions = gd.build()
        # st.write("Data yang ditampilkan berdasarkan file data produk yang diupload yaitu 1 tahun terakhir dari 01-Februari-2022 s/d 28-Februari-2023")
        category = st.radio(
            "Informasi Yang Diinginkan",
            ('Total Order','Produk Yang Belum Lama Terjual',
             'Produk Yang Banyak Terjual','Produk Yang Banyak Memberikan Keuntungan'))

        if category == 'Total Order':
            totalOrder = getTotalOrder(data)
            st.write('Total Order Keseluruhan Sebanyak ',totalOrder)
        elif category == 'Produk Yang Belum Lama Terjual':
            st.write('Total Produk Yang Belum Lama Terjual Sebanyak ',len(rfm[rfm['Recency'] == rfm['Recency'].min()]))
            st.write(rfm[rfm['Recency'] == rfm['Recency'].min()])
            # gd = GridOptionsBuilder.from_dataframe(rfm[rfm['Recency'] == rfm['Recency'].min()])
            # gd.configure_pagination(enabled=True,paginationPageSize=10)
            # # gd.configure_side_bar()
            # gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True,filterable=True)
            # gridOptions = gd.build()
            # AgGrid(rfm[rfm['Recency'] == rfm['Recency'].min()], gridOptions=gridOptions)
        elif category == 'Produk Yang Banyak Terjual':
            st.write('Total Produk Yang Banyak Terjual Sebanyak ',len(rfm[rfm['Frequency'] == rfm['Frequency'].max()]))
            st.write(rfm[rfm['Frequency'] == rfm['Frequency'].max()])
        elif category == 'Produk Yang Banyak Memberikan Keuntungan':
            st.write('Total Produk Yang Banyak Memberikan Keuntungan Sebanyak ',len(rfm[rfm['Monetary'] == rfm['Monetary'].max()]))
            st.write(rfm[rfm['Monetary'] == rfm['Monetary'].max()])
            # gd = GridOptionsBuilder.from_dataframe(rfm[rfm['Monetary'] == rfm['Monetary'].max()])
            # gd.configure_pagination(enabled=True)
            # gd.configure_side_bar()
            # gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            # gridOptions = gd.build()
            # AgGrid(rfm[rfm['Monetary'] == rfm['Monetary'].max()], gridOptions=gridOptions)

        # st.write(data)
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
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
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
    