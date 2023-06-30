import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score
from sklearn_extra.cluster import KMedoids
import string
import seaborn as sns
import matplotlib.pyplot as plt

def app(rfm):
    Q1 = rfm['Frequency'].quantile(0.25)
    Q3 = rfm['Frequency'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR
    lower_array = rfm.loc[rfm['Frequency']<=upper].index
    rfm.drop(index=lower_array, inplace=True)
    rfmkmeans = rfm
    rfmkmedoid = rfm

    st.write("Data yang ditampilkan berdasarkan file data produk yang diupload yaitu 1 tahun terakhir dari 01-Februari-2022 s/d 28-Februari-2023")
    st.write("Silahkan Pilih Algoritma Klaster Yang Ingin Digunakan")
    category = st.radio(
        "Klaster",
        ('K-Means','K-medoids'))

    if category == 'K-Means':
        rfmkmeans.drop('Last Order Date', axis = 1, inplace = True)
        rfmkmeans.drop('Monetary', axis = 1, inplace = True)
        rfmkmeans.drop('Tenure', axis = 1, inplace = True)
        rfmkmeans.astype({'Recency':'float64','Frequency':'float64'})

        
        scalerkmeans = StandardScaler()
        x_scaledkmeans=scalerkmeans.fit(rfmkmeans)
        x_scaledkmeans = scalerkmeans.fit_transform(rfmkmeans)

        
        kmeans_scaled = KMeans(3)
        kmeans_scaled.fit(x_scaledkmeans)
        identified_clusters = kmeans_scaled.fit_predict(rfmkmeans)
        clusters_scaled = rfmkmeans.copy()
        clusters_scaled2 = rfmkmeans.copy()
        clusters_scaled['Cluster_Kmeans']=kmeans_scaled.fit_predict(x_scaledkmeans)
        
        labels = kmeans_scaled.labels_
        
        st.write('DBI Score Untuk K-Means adalah ',davies_bouldin_score(x_scaledkmeans, labels))
    elif category == 'K-medoids':
        rfmkmedoid.drop('Last Order Date', axis = 1, inplace = True)
        rfmkmedoid.drop('Monetary', axis = 1, inplace = True)
        rfmkmedoid.drop('Tenure', axis = 1, inplace = True)
        rfmkmedoid.astype({'Recency':'float64','Frequency':'float64'})

        scaler = StandardScaler()
        x_scaled=scaler.fit(rfmkmedoid)
        x_scaled = scaler.fit_transform(rfmkmedoid)

        
        kmedoids = KMedoids(n_clusters=3).fit(x_scaled)
        rfmkmedoid.insert(0, 'Cluster', kmedoids.labels_)
        db_index = davies_bouldin_score(rfmkmedoid, kmedoids.labels_)
        st.write('DBI Score Untuk K-Medoids adalah ',db_index)
        rfmkmedoid['ClusterInt'] = rfmkmedoid['Cluster']
        rfmkmedoid['Cluster'] = rfmkmedoid['Cluster'].astype(str)
        rfmkmedoid.dtypes
        rfmkmedoid['Cluster'] = rfmkmedoid['Cluster'].replace(['0','1','2'],['Banyak Terjual','Cukup Terjual','Sedikit Terjual'])

        fig = plt.figure
        savefig = plt.savefig('kmedoids.png')
        sns.scatterplot(x=rfmkmedoid['Recency'], y=rfmkmedoid['Frequency'], hue = rfmkmedoid['Cluster'], palette="Set2", s = 100, alpha = 0.7)
        st.pyplot(savefig)
        