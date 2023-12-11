import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import numpy as np

st.set_page_config(layout="wide")

st.sidebar.code("""
    !pip install matplotlib
""")

url = "https://docs.google.com/spreadsheets/d/1D_XqlIYDrrSvi54C5WSJkIwHQJje_mq_lS1xRTxAPpQ/gviz/tq?tqx=out:csv&sheet=Survey_Perilaku_Saling_Peduli_dan_Saling_Jaga_Integritas_Versi_2"
# data_raw = pd.read_csv('Hasil Survei Aplikasi J3Li - Sheet1.csv')
df = pd.read_csv(url, usecols=range(21))
time = pd.read_csv(url, usecols=range(23))
time = pd.to_datetime(time['Submitted At']).max()
time = time + pd.Timedelta(hours=7)
st.write(f'last updated: {time}')

lookup = {
    "Sangat Tidak Setuju" : 1,
    "Tidak Setuju" : 2,
    "Ragu-Ragu" : 3,
    "Setuju" : 4,
    "Sangat Setuju" : 5
}

df.loc[df['Jabatan'].str.contains('Utama'),'Jabatan'] = 'Eselon II'
df.loc[df['Jabatan'].str.contains('Madya'),'Jabatan'] = 'Eselon III'
df.loc[df['Jabatan'].str.contains('Muda'),'Jabatan'] = 'Eselon IV'
df.loc[df['Jabatan'].str.contains('Pelaksana'),'Jabatan'] = 'Pelaksana'

df = df.replace(lookup)
df.columns = range(21)

outlier_df = df[(df[range(13,16)].mean(axis=1) < 3) & (df[16] < 3) | (df[range(13,16)].mean(axis=1) > 3) & (df[16] > 3)]

st.write("Data yang terkumpul:")
df_pivot_awal = df.copy()
df_pivot_awal = df_pivot_awal[[0,1,2,3]]
df_pivot_awal.columns = ['unit_kerja','satu', 'dua', 'tiga']
pivot_awal = pd.crosstab(index=df_pivot_awal['unit_kerja'], columns=df_pivot_awal['satu'], margins=True, margins_name='Total', dropna=False)
st.write(pivot_awal)
st.write(f"Dari {df.shape[0]} baris data yang diterima, terdapat {outlier_df.shape[0]} outlier sehingga data yang diproses selanjutnya berjumlah {df.shape[0]-outlier_df.shape[0]}")

reverse = {
    5 : 1,
    4 : 2,
    2 : 4,
    1 : 5
}


df1 = df.copy()
df1 = df1.drop(outlier_df.index)
df1[16] = df1[16].replace(reverse)

st.title("Info Responden")
df_pivot = df1.copy()
df_pivot = df_pivot[[0,1,2,3]]
df_pivot.columns = ['unit_kerja','satu', 'dua', 'tiga']

pivot_kota = pd.crosstab(index=df_pivot['unit_kerja'], columns=df_pivot['satu'], margins=True, margins_name='Total', dropna=False)
st.subheader("Sebaran Kota per Unit Eselon I")
st.write(pivot_kota)
pivot_jabatan = pd.crosstab(index=df_pivot['unit_kerja'], columns=df_pivot['dua'], margins=True, margins_name='Total', dropna=False)
st.subheader("Sebaran Jabatan per Unit Eselon I")
st.write(pivot_jabatan)
pivot_generasi = pd.crosstab(index=df_pivot['unit_kerja'], columns=df_pivot['tiga'], margins=True, margins_name='Total', dropna=False)
st.subheader("Sebaran Kelompok Usia per Unit Eselon I")
st.write(pivot_generasi)


# Sidebar with user inputs for main section
# anchor = st.sidebar.selectbox('Select Anchor', ['unit kerja', 'kota', 'jabatan', 'kelompok usia'])
st.sidebar.title("Filter Result")
# if anchor == 'kota':
#     unit_kerja = st.sidebar.multiselect('Select Unit Kerja', df1[0].unique(), default=df1[0].unique())
#     # kota = st.sidebar.multiselect('Select Kota', df1[1].unique(), default=df1[1].unique())
#     jabatan = st.sidebar.multiselect('Select Jabatan', df1[2].unique(), default=df1[2].unique())
#     generasi = st.sidebar.multiselect('Select Kelompok Usia', df1[3].unique(), default=df1[3].unique())
# elif anchor == 'jabatan':
#     unit_kerja = st.sidebar.multiselect('Select Unit Kerja', df1[0].unique(), default=df1[0].unique())
#     kota = st.sidebar.multiselect('Select Kota', df1[1].unique(), default=df1[1].unique())
#     # jabatan = st.sidebar.multiselect('Select Jabatan', df1[2].unique(), default=df1[2].unique())
#     generasi = st.sidebar.multiselect('Select Kelompok Usia', df1[3].unique(), default=df1[3].unique())
# elif anchor == 'kelompok usia':
#     unit_kerja = st.sidebar.multiselect('Select Unit Kerja', df1[0].unique(), default=df1[0].unique())
#     kota = st.sidebar.multiselect('Select Kota', df1[1].unique(), default=df1[1].unique())
#     jabatan = st.sidebar.multiselect('Select Jabatan', df1[2].unique(), default=df1[2].unique())
#     # generasi = st.sidebar.multiselect('Select Kelompok Usia', df1[3].unique(), default=df1[3].unique())
# else:
# unit_kerja = st.sidebar.multiselect('Select Unit Kerja', df1[0].unique(), default=df1[0].unique())
kota = st.sidebar.multiselect('Select Kota', df1[1].unique(), default=df1[1].unique())
jabatan = st.sidebar.multiselect('Select Jabatan', df1[2].unique(), default=df1[2].unique())
generasi = st.sidebar.multiselect('Select Kelompok Usia', df1[3].unique(), default=df1[3].unique())

# "Refresh" button to trigger calculation
refresh_button = st.sidebar.button("Refresh")

if refresh_button:
    # idx_unit_kerja = set(df1[df1[0].isin(unit_kerja)].index)
    idx_kota = set(df1[df1[1].isin(kota)].index)
    idx_jabatan = set(df1[df1[2].isin(jabatan)].index)
    idx_generasi = set(df1[df1[3].isin(generasi)].index)
    all_idx = list(set.intersection(idx_kota, idx_jabatan, idx_generasi))
    df1 = df1.loc[all_idx]


st.title("Analisis Hasil Survei")

x1 = df1[range(8,8+5)].mean(axis=1)
x2 = df1[range(13,13+4)].mean(axis=1)
x3 = df1[range(17,17+3)].mean(axis=1)
perlu = df1[18]
niat = df1[7]
y = df1[range(4,4+4)].mean(axis=1)

# def show_result(df, group_col, display_col):
#     averages_df = df.groupby(group_col).agg({group_col: 'count', 'Sikap (X1)': 'mean', 'Norma Sosial (X2)': 'mean', 'Kontrol Perilaku (X3)': 'mean', 'Niat (y)': 'mean', 'Perlu J3Li': 'mean', 'Niat Menggunakan J3Li': 'mean'})
#     averages_df = averages_df.rename_axis(display_col)
#     averages_df = averages_df.round(3).astype(float)
#     averages_df = averages_df.rename(columns={averages_df.columns[0]: "Jml Responden"})

#     # Set up Seaborn heatmap
#     plt.figure(figsize=(10, 6))
#     sns.set(font_scale=1)
#     sns.heatmap(averages_df.drop(columns=[display_col, "Jml Responden"]).T, cmap='RdYlGn', annot=True, linewidths=.5, cbar_kws={"orientation": "horizontal"})

#     # Display the heatmap
#     st.pyplot()

# Disable PyplotGlobalUseWarning
warnings.filterwarnings("ignore", category=UserWarning)
st.set_option('deprecation.showPyplotGlobalUse', False)

def show_result(df, group_col, display_col, header):
    averages_df = df.groupby(group_col).agg({'Sikap (X1)': 'mean', 'Norma Sosial (X2)': 'mean', 'Kontrol Perilaku (X3)': 'mean', 'Niat (y)': 'mean', 'Perlu J3Li': 'mean', 'Niat Menggunakan J3Li': 'mean'})
    averages_df = averages_df.rename_axis(display_col)
    averages_df = averages_df.round(3).astype(float)
    
    # Set up Seaborn heatmap
    plt.figure(figsize=(10, 6))
    sns.set(font_scale=1)
    
    # Specify the number format for annotations
    fmt = ".3f"

    # Create a custom heatmap with Seaborn
    heatmap = sns.heatmap(averages_df, cmap='RdYlGn', annot=True, fmt=fmt, linewidths=.5, cbar_kws={"orientation": "horizontal"})

    # Display the header
    plt.title(header)

    # Customize x-tick labels to wrap to the next line
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=0, ha='center', fontsize=10)
    
    # Display the heatmap
    st.pyplot()

df3 = df1.copy()
df3['Sikap (X1)'] = x1
df3['Norma Sosial (X2)'] = x2
df3['Kontrol Perilaku (X3)'] = x3
df3['Niat (y)'] = y
df3['Perlu J3Li'] = perlu
df3['Niat Menggunakan J3Li'] = niat

st.write(f'Kota: {kota}')
show_result(df3, 0, 'Unit Kerja', "Sebaran Per Unit Kerja")
show_result(df3, 1, 'Kota', "Sebaran Per Unit Kota Survei")
show_result(df3, 2, 'Jabatan', "Sebaran Per Kelompok Jabatan")
show_result(df3, 3, 'Generasi', "Sebaran Per Kelompok Usia")
