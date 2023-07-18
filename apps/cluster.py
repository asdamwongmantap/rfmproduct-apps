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
from apps import analyze
from sklearn.metrics import davies_bouldin_score

def app(rfm):
    st.write("Sebelum memilih metode klaster, pastikan anda telah mengupload file csv yang didapat dari datawarehouse !")

    option = st.selectbox(
    'Silahkan Pilih Metode Klaster !',
    ('-', 'K-Medoids', 'K-Means'))

    if option == 'K-Medoids':
        productcluster(option,rfm)
    elif option == 'K-Means':
        productcluster(option,rfm)
    

def productcluster(cluster,rfm):
    Q1 = rfm['Frequency'].quantile(0.25)
    Q3 = rfm['Frequency'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR
    lower_array = rfm.loc[rfm['Frequency']<=upper].index
    rfm.drop(index=lower_array, inplace=True)
    rfmkmeans = rfm
    rfmkmedoid = rfm

    if cluster == 'K-Means':
        isAutoCluster = st.radio(
            "Apakah ingin melakukan penentuan klaster secara otomatis ?",
            ('Ya','Tidak'))
       
        rfmkmeans.drop('Last Order Date', axis = 1, inplace = True)
        rfmkmeans.drop('Monetary', axis = 1, inplace = True)
        rfmkmeans.drop('Tenure', axis = 1, inplace = True)
        rfmkmeans.astype({'Recency':'float64','Frequency':'float64'})

        
        scalerkmeans = StandardScaler()
        x_scaledkmeans=scalerkmeans.fit(rfmkmeans)
        x_scaledkmeans = scalerkmeans.fit_transform(rfmkmeans)

        if isAutoCluster == 'Ya':
            numOfCluster = clusterbydbikmeans(x_scaledkmeans)['Klaster']
        else:
            numOfCluster = st.number_input('Masukkan Jumlah Klaster Yang Diinginkan!', min_value=2, max_value=10, value=2, step=1)
            if int(numOfCluster) <= 0:
                st.write("Jumlah klaster harus lebih dari 0")

        st.write(clusterbydbikmeans(x_scaledkmeans)['Klaster'])

        if int(numOfCluster) != 0:
            kmeans_scaled = KMeans(int(numOfCluster))
            kmeans_scaled.fit(x_scaledkmeans)
            identified_clusters = kmeans_scaled.fit_predict(rfmkmeans)
            clusters_scaled = rfmkmeans.copy()
            # clusters_scaled2 = rfmkmeans.copy()
            clusters_scaled['Cluster_Kmeans']=kmeans_scaled.fit_predict(x_scaledkmeans)
        
            
            labels = kmeans_scaled.labels_
            
            # st.write('DBI Score Untuk K-Means adalah ',davies_bouldin_score(x_scaledkmeans, labels))
            if isAutoCluster == 'Ya':
                 clusters_scaled['Cluster_Kmeans'] = clusters_scaled['Cluster_Kmeans'].astype(str)
                 clusters_scaled['Cluster_Kmeans'] = clusters_scaled['Cluster_Kmeans'].replace(['0','1','2','3'],['Cukup Terjual','Sedikit Terjual','Lumayan Terjual','Banyak Terjual'])
            else:
                 clusters_scaled['Cluster_Kmeans']=kmeans_scaled.fit_predict(x_scaledkmeans)

            st.set_option('deprecation.showPyplotGlobalUse', False)
            fig = plt.figure
            savefig = plt.savefig('kmeans.png')
            sns.scatterplot(x=clusters_scaled['Recency'], y=clusters_scaled['Frequency'], 
                            hue = clusters_scaled['Cluster_Kmeans'], palette="Set2", s = 100, alpha = 0.7)
            st.pyplot(savefig)
    elif cluster == 'K-Medoids':
        isAutoCluster = st.radio(
            "Apakah ingin melakukan penentuan klaster secara otomatis ?",
            ('Ya','Tidak'))
       
        rfmkmedoid.drop('Last Order Date', axis = 1, inplace = True)
        rfmkmedoid.drop('Monetary', axis = 1, inplace = True)
        rfmkmedoid.drop('Tenure', axis = 1, inplace = True)
        rfmkmedoid.astype({'Recency':'float64','Frequency':'float64'})

        scaler = StandardScaler()
        x_scaled=scaler.fit(rfmkmedoid)
        x_scaled = scaler.fit_transform(rfmkmedoid)

        # st.warning(clusterbydbikmedoids(x_scaled))
        if isAutoCluster == 'Ya':
            numOfCluster = clusterbydbikmedoids(x_scaled)['Klaster']
        else:
            numOfCluster = st.number_input('Masukkan Jumlah Klaster Yang Diinginkan!', min_value=2, max_value=10, value=2, step=1)
            if int(numOfCluster) <= 0:
                st.write("Jumlah klaster harus lebih dari 0")

        if int(numOfCluster) != 0:
            kmedoids = KMedoids(n_clusters=int(numOfCluster)).fit(x_scaled)
            rfmkmedoid.insert(0, 'Cluster', kmedoids.labels_)
            # db_index = davies_bouldin_score(rfmkmedoid, kmedoids.labels_)
            # st.write('DBI Score Untuk K-Medoids adalah ',db_index)
            # rfmkmedoid['ClusterInt'] = rfmkmedoid['Cluster']
            if isAutoCluster == 'Ya':
                rfmkmedoid['Cluster'] = rfmkmedoid['Cluster'].astype(str)
                # rfmkmedoid.dtypes
                rfmkmedoid['Cluster'] = rfmkmedoid['Cluster'].replace(['0','1'],['Sedikit Terjual','Banyak Terjual'])
            else:
                rfmkmedoid['Cluster'] = kmedoids.labels_
            st.set_option('deprecation.showPyplotGlobalUse', False)

            fig = plt.figure
            savefig = plt.savefig('kmedoids.png')
            sns.scatterplot(x=rfmkmedoid['Recency'], y=rfmkmedoid['Frequency'], hue = rfmkmedoid['Cluster'], palette="Set2", s = 100, alpha = 0.7)
            st.pyplot(savefig)

def clusterbydbikmedoids(x_scaled):
    dbikmedoid = pd.DataFrame({"Klaster":[],"DBI":[]})
    dbikmedoidklaster = []
    dbikmedoiddbi = []

    for i in [2,3,4,5,6]:
        kmedoids = KMedoids(n_clusters=i).fit(x_scaled)
        db_index = davies_bouldin_score(x_scaled, kmedoids.labels_)
        dbikmedoidklaster.append(i)
        dbikmedoiddbi.append(db_index)

    dbikmedoid['Klaster'] = dbikmedoidklaster
    dbikmedoid['DBI'] = dbikmedoiddbi

    return dbikmedoid[dbikmedoid['DBI'] == dbikmedoid['DBI'].min()]

def clusterbydbikmeans(x_scaledkmeans):
    dbikmeans = pd.DataFrame({"Klaster":[],"DBI":[]})
    dbikmeansklaster = []
    dbikmeansdbi = []

    for i in [2,3,4,5,6]:
        kmeans_scaled = KMeans(n_clusters=i,n_init='auto',init='k-means++')
        kmeans_scaled.fit(x_scaledkmeans)
        labels = kmeans_scaled.labels_
        dbikmeansklaster.append(i)
        dbikmeansdbi.append(davies_bouldin_score(x_scaledkmeans, labels))

    dbikmeans['Klaster'] = dbikmeansklaster
    dbikmeans['DBI'] = dbikmeansdbi

    return dbikmeans[dbikmeans['DBI'] == dbikmeans['DBI'].min()]
        