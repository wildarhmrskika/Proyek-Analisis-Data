import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
from sklearn.ensemble import IsolationForest

# Fungsi untuk memuat data day.csv
def load_day_data():
    file_path_day = r'dashboard/day.csv'
    if os.path.exists(file_path_day):
        df_day = pd.read_csv(file_path_day)
        return df_day
    else:
        st.error(f"File {file_path_day} tidak ditemukan.")
        return None

# Fungsi untuk memuat data hour.csv
def load_hour_data():
    file_path_hour = r'dashboard/hour.csv'
    if os.path.exists(file_path_hour):
        df_hour = pd.read_csv(file_path_hour)
        return df_hour
    else:
        st.error(f"File {file_path_hour} tidak ditemukan.")
        return None

# Apply custom CSS for styling
def apply_custom_css():
    st.markdown("""
    <style>
    /* General app background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8, #d9e4ec);
        color: #333333;
        font-family: 'Arial', sans-serif;
    }

    /* Customizing the sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #4A7BF7, #67C3F3);
        color: white;
    }

    /* Title styling */
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
        font-weight: 600;
        color: #1f77b4;
    }

    /* Custom buttons */
    button {
        background-color: #4A7BF7 !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        margin-top: 15px;
    }

    button:hover {
        background-color: #5A9CF7 !important;
        color: white !important;
    }

    /* Styling charts and tables */
    .stPlotlyChart, .stDataFrame {
        border-radius: 12px;
        background-color: white;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Content text styling */
    p, label, .stMarkdown {
        font-family: 'Arial', sans-serif;
        color: #333333;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
apply_custom_css()

# Seaborn theme settings
sns.set_theme(style="whitegrid")

# Title and Description
st.title("🚴‍♂️ **Dashboard Penyewaan Sepeda**")
st.markdown("""
**Analisis data penyewaan sepeda untuk melihat tren berdasarkan hari kerja, akhir pekan, hari libur, dan jam tertentu.** 
""")

# Sidebar for navigation
st.sidebar.title("🌟 Navigasi")
st.sidebar.write("Pilih opsi analisis yang tersedia di bawah:")
option = st.sidebar.selectbox("Pilih Analisis", 
                            ["Perbandingan Hari Kerja vs Akhir Pekan", 
                            "Pengaruh Hari Libur", 
                            "Penyewaan Berdasarkan Jam",
                            "Deteksi Anomali (Z-score)",
                            "Deteksi Anomali (Isolation Forest)",
                            "Rata-rata Penyewaan Berdasarkan Cuaca"])

# Load data
df_day_cleaned = load_day_data()

# Perbandingan Hari Kerja vs Akhir Pekan
if option == "Perbandingan Hari Kerja vs Akhir Pekan" and df_day_cleaned is not None:
    st.header("📅 Perbandingan Jumlah Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")
    
    avg_rentals = df_day_cleaned.groupby('workingday')['cnt'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='workingday', y='cnt', data=avg_rentals, palette='Spectral', ax=ax)
    ax.set_title('Rata-rata Penyewaan: Hari Kerja vs Akhir Pekan', fontsize=16)
    ax.set_xticklabels(['Akhir Pekan', 'Hari Kerja'])
    ax.set_xlabel('Hari', fontsize=12)
    ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
    st.pyplot(fig)

    st.write("Rata-rata penyewaan sepeda pada hari kerja dan akhir pekan:")
    st.write(avg_rentals)

# Pengaruh Hari Libur
elif option == "Pengaruh Hari Libur" and df_day_cleaned is not None:
    st.header("🏖️ Pengaruh Hari Libur terhadap Jumlah Penyewaan Sepeda")

    avg_rentals_holiday = df_day_cleaned.groupby('holiday')['cnt'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='holiday', y='cnt', data=avg_rentals_holiday, palette='coolwarm', ax=ax)
    ax.set_title('Rata-rata Penyewaan Sepeda: Hari Libur vs Non-Hari Libur', fontsize=16)
    ax.set_xticklabels(['Non-Hari Libur', 'Hari Libur'])
    ax.set_xlabel('Status Hari', fontsize=12)
    ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
    st.pyplot(fig)

    st.write("Rata-rata penyewaan sepeda pada hari libur dan non-hari libur:")
    st.write(avg_rentals_holiday)

# Penyewaan Berdasarkan Jam
elif option == "Penyewaan Berdasarkan Jam":
    st.header("⏰ Penyewaan Sepeda Berdasarkan Jam")

    df_hour = load_hour_data()

    if df_hour is not None:
        avg_rentals_per_hour = df_hour.groupby('hr')['cnt'].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x='hr', y='cnt', data=avg_rentals_per_hour, marker='o', ax=ax, color="green")
        ax.set_title('Rata-rata Penyewaan Sepeda per Jam', fontsize=16)
        ax.set_xlabel('Jam', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
        st.pyplot(fig)

        st.write("Rata-rata penyewaan sepeda per jam:")
        st.write(avg_rentals_per_hour)

# Deteksi Anomali menggunakan Z-score
elif option == "Deteksi Anomali (Z-score)" and df_day_cleaned is not None:
    st.header("⚠️ Deteksi Anomali Penyewaan Sepeda dengan Z-score")

    daily_rentals = df_day_cleaned[['dteday', 'cnt']]
    daily_rentals['dteday'] = pd.to_datetime(daily_rentals['dteday'])

    # Menghitung Z-score
    z_scores = stats.zscore(daily_rentals['cnt'])

    # Ambil anomali dengan Z-score lebih dari 3 atau kurang dari -3
    anomalies_z = daily_rentals[(z_scores > 3) | (z_scores < -3)]
    
    # Visualisasi dengan anomali terdeteksi
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(daily_rentals['dteday'], daily_rentals['cnt'], marker='o', color='b', label='Jumlah Penyewaan')
    ax.scatter(anomalies_z['dteday'], anomalies_z['cnt'], color='red', label='Anomali', zorder=5)
    ax.set_title('Jumlah Penyewaan Sepeda per Hari dengan Anomali (Z-score)', fontsize=16)
    ax.set_xlabel('Tanggal', fontsize=12)
    ax.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid()
    plt.axhline(daily_rentals['cnt'].mean(), color='red', linestyle='--', label='Rata-rata Penyewaan')
    ax.legend()
    st.pyplot(fig)

    if not anomalies_z.empty:
        st.write("📋 Anomali yang Ditemukan dengan Z-score:")
        st.dataframe(anomalies_z)
    else:
        st.write("Tidak ada anomali yang terdeteksi dengan metode Z-score.")

# Deteksi Anomali menggunakan Isolation Forest
elif option == "Deteksi Anomali (Isolation Forest)" and df_day_cleaned is not None:
    st.header("⚠️ Deteksi Anomali Penyewaan Sepeda dengan Isolation Forest")

    daily_rentals = df_day_cleaned[['dteday', 'cnt']]
    daily_rentals['dteday'] = pd.to_datetime(daily_rentals['dteday'])

    # Menggunakan Isolation Forest untuk mendeteksi anomali
    iso_forest = IsolationForest(contamination=0.1)
    daily_rentals['anomaly'] = iso_forest.fit_predict(daily_rentals[['cnt']])

    # Memisahkan anomali dari data normal
    anomalies_iso = daily_rentals[daily_rentals['anomaly'] == -1]

    # Visualisasi dengan anomali terdeteksi
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(daily_rentals['dteday'], daily_rentals['cnt'], marker='o', color='b', label='Jumlah Penyewaan')
    ax.scatter(anomalies_iso['dteday'], anomalies_iso['cnt'], color='red', label='Anomali', zorder=5)
    ax.set_title('Jumlah Penyewaan Sepeda per Hari dengan Anomali (Isolation Forest)', fontsize=16)
    ax.set_xlabel('Tanggal', fontsize=12)
    ax.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid()
    plt.axhline(daily_rentals['cnt'].mean(), color='red', linestyle='--', label='Rata-rata Penyewaan')
    ax.legend()
    st.pyplot(fig)

    if not anomalies_iso.empty:
        st.write("📋 Anomali yang Ditemukan dengan Isolation Forest:")
        st.dataframe(anomalies_iso)
    else:
        st.write("Tidak ada anomali yang terdeteksi dengan metode Isolation Forest.")

# Rata-rata Penyewaan Berdasarkan Cuaca
elif option == "Rata-rata Penyewaan Berdasarkan Cuaca" and df_day_cleaned is not None:
    st.header("☀️ Rata-rata Penyewaan Berdasarkan Kondisi Cuaca")

    avg_rentals_weather = df_day_cleaned.groupby('weathersit')['cnt'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='weathersit', y='cnt', data=avg_rentals_weather, palette='Blues', ax=ax)
    ax.set_title('Rata-rata Penyewaan Berdasarkan Kondisi Cuaca', fontsize=16)
    ax.set_xticklabels(['Cerah', 'Berkabut', 'Hujan', 'Badai'], rotation=45)
    ax.set_xlabel('Kondisi Cuaca', fontsize=12)
    ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
    st.pyplot(fig)

    st.write("Rata-rata penyewaan sepeda berdasarkan kondisi cuaca:")
    st.write(avg_rentals_weather)
