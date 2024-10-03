import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
from sklearn.ensemble import IsolationForest

# Fungsi untuk memuat data day.csv
def load_day_data():
    file_path_day = r'Bike-sharing-dataset/day.csv'
    if os.path.exists(file_path_day):
        df_day = pd.read_csv(file_path_day)
        return df_day
    else:
        st.error(f"File {file_path_day} tidak ditemukan.")
        return None

# Fungsi untuk memuat data hour.csv
def load_hour_data():
    file_path_hour = r'Bike-sharing-dataset/hour.csv'
    if os.path.exists(file_path_hour):
        df_hour = pd.read_csv(file_path_hour)
        return df_hour
    else:
        st.error(f"File {file_path_hour} tidak ditemukan.")
        return None

# Menyiapkan kolom 'dateday' untuk pengolahan data berdasarkan tanggal
def prepare_date_column(df):
    if 'dteday' in df.columns:
        df['dateday'] = pd.to_datetime(df['dteday'])
    elif {'year', 'month', 'day'}.issubset(df.columns):
        df['dateday'] = pd.to_datetime(df[['year', 'month', 'day']])
    else:
        st.error("Tidak ditemukan kolom 'dateday', atau kolom lain yang memungkinkan pembentukan tanggal.")
    return df

# Load the data
day_df = load_day_data()

# Check if the dataframe is not None before proceeding
if day_df is not None:
    # Prepare the 'dateday' column
    day_df = prepare_date_column(day_df)

    with st.sidebar:
        # Menambahkan gambar di sidebar
        st.image("https://github.com/wildarhmrskika/Proyek-Analisis-Data/blob/main/assets/pngtree-cartoon-characters-ride-bicycles-png-image_4141664.jpg")

    # Sidebar untuk pemilihan periode waktu
    st.sidebar.title('🗓 Pilih Periode Waktu')
    start_date = st.sidebar.date_input("Pilih Tanggal Mulai", pd.to_datetime('2011-01-01'))
    end_date = st.sidebar.date_input("Pilih Tanggal Akhir", pd.to_datetime('2012-12-31'))

    # Menyaring dataset berdasarkan periode waktu yang dipilih
    def filter_data_by_date(df, start_date, end_date):
        # Check if 'dateday' exists in the dataframe
        if 'dateday' in df.columns:
            filtered_df = df[(df['dateday'] >= pd.to_datetime(start_date)) & (df['dateday'] <= pd.to_datetime(end_date))]
            return filtered_df
        else:
            st.error("Kolom 'dateday' tidak ditemukan.")
            return df

    filtered_day_df = filter_data_by_date(day_df, start_date, end_date)

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
    df_day_cleaned = day_df.copy()

    # Perbandingan Hari Kerja vs Akhir Pekan
    if option == "Perbandingan Hari Kerja vs Akhir Pekan":
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
    elif option == "Pengaruh Hari Libur":
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
    elif option == "Deteksi Anomali (Z-score)":
        st.header("📊 Deteksi Anomali Menggunakan Z-score")

        # Hitung Z-score untuk setiap baris data pada kolom 'cnt'
        df_day_cleaned['z_score'] = stats.zscore(df_day_cleaned['cnt'])

        # Tandai baris-baris yang merupakan anomali (nilai Z-score lebih besar dari threshold)
        threshold = 3
        anomalies = df_day_cleaned[df_day_cleaned['z_score'].abs() > threshold]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(x='dteday', y='cnt', data=df_day_cleaned, ax=ax, label='Normal Data')
        sns.scatterplot(x='dteday', y='cnt', data=anomalies, ax=ax, color='red', label='Anomali')
        ax.set_title('Deteksi Anomali Penyewaan Sepeda dengan Z-score', fontsize=16)
        ax.set_xlabel('Tanggal', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan', fontsize=12)
        st.pyplot(fig)

        st.write(f"Jumlah total anomali yang terdeteksi: {len(anomalies)}")
        st.write(anomalies[['dteday', 'cnt', 'z_score']])

    # Deteksi Anomali menggunakan Isolation Forest
    elif option == "Deteksi Anomali (Isolation Forest)":
        st.header("📉 Deteksi Anomali Menggunakan Isolation Forest")

        # Menyiapkan model Isolation Forest
        model = IsolationForest(contamination=0.01, random_state=42)
        df_day_cleaned['anomaly_if'] = model.fit_predict(df_day_cleaned[['cnt']])

        # Filter data yang dianggap sebagai anomali
        anomalies_if = df_day_cleaned[df_day_cleaned['anomaly_if'] == -1]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(x='dteday', y='cnt', data=df_day_cleaned, ax=ax, label='Normal Data')
        sns.scatterplot(x='dteday', y='cnt', data=anomalies_if, ax=ax, color='orange', label='Anomali')
        ax.set_title('Deteksi Anomali Penyewaan Sepeda dengan Isolation Forest', fontsize=16)
        ax.set_xlabel('Tanggal', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan', fontsize=12)
        st.pyplot(fig)

        st.write(f"Jumlah total anomali yang terdeteksi: {len(anomalies_if)}")
        st.write(anomalies_if[['dteday', 'cnt']])

    # Rata-rata Penyewaan Berdasarkan Cuaca
    elif option == "Rata-rata Penyewaan Berdasarkan Cuaca":
        st.header("☀️ Rata-rata Penyewaan Sepeda Berdasarkan Cuaca")

        # Mengelompokkan data berdasarkan cuaca (weathersit) dan menghitung rata-rata penyewaan
        avg_rentals_weather = df_day_cleaned.groupby('weathersit')['cnt'].mean().reset_index()

        # Definisikan label cuaca
        weather_labels = {
            1: "Cerah/Sedikit Berawan",
            2: "Mendung",
            3: "Salju/Hujan Ringan",
            4: "Cuaca Ekstrim"
        }
        avg_rentals_weather['weathersit'] = avg_rentals_weather['weathersit'].map(weather_labels)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x='weathersit', y='cnt', data=avg_rentals_weather, palette='coolwarm', ax=ax)
        ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca', fontsize=16)
        ax.set_xlabel('Kondisi Cuaca', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
        st.pyplot(fig)

        st.write("Rata-rata penyewaan sepeda berdasarkan kondisi cuaca:")
        st.write(avg_rentals_weather)

# Jika tidak ada data yang di-load
else:
    st.error("Data tidak tersedia. Harap pastikan file data ada di folder 'Bike-sharing-dataset'.")
    # Analisis Penyewaan Berdasarkan Hari Kerja
    elif option == "Penyewaan Berdasarkan Hari Kerja":
        st.header("📅 Penyewaan Berdasarkan Hari Kerja")

        # Mengelompokkan data berdasarkan apakah itu hari kerja atau akhir pekan
        avg_rentals_workingday = df_day_cleaned.groupby('workingday')['cnt'].mean().reset_index()

        # Mapping untuk label hari kerja
        workingday_labels = {
            0: "Akhir Pekan",
            1: "Hari Kerja"
        }
        avg_rentals_workingday['workingday'] = avg_rentals_workingday['workingday'].map(workingday_labels)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x='workingday', y='cnt', data=avg_rentals_workingday, palette='viridis', ax=ax)
        ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Hari Kerja vs Akhir Pekan', fontsize=16)
        ax.set_xlabel('Kategori Hari', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
        st.pyplot(fig)

        st.write("Rata-rata penyewaan sepeda berdasarkan hari kerja vs akhir pekan:")
        st.write(avg_rentals_workingday)

    # Analisis Penyewaan Berdasarkan Jenis Pengguna
    elif option == "Penyewaan Berdasarkan Jenis Pengguna":
        st.header("👥 Penyewaan Berdasarkan Jenis Pengguna")

        # Mengelompokkan data berdasarkan jenis pengguna (casual vs registered)
        avg_rentals_user_type = df_day_cleaned[['casual', 'registered', 'cnt']].mean().reset_index()

        # Menampilkan bar chart dari rata-rata penyewaan oleh pengguna casual dan registered
        user_type_data = {
            'User Type': ['Casual', 'Registered'],
            'Average Rentals': [avg_rentals_user_type[avg_rentals_user_type['index'] == 'casual']['cnt'].values[0],
                                avg_rentals_user_type[avg_rentals_user_type['index'] == 'registered']['cnt'].values[0]]
        }
        user_type_df = pd.DataFrame(user_type_data)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x='User Type', y='Average Rentals', data=user_type_df, palette='magma', ax=ax)
        ax.set_title('Rata-rata Penyewaan Berdasarkan Jenis Pengguna (Casual vs Registered)', fontsize=16)
        ax.set_xlabel('Jenis Pengguna', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
        st.pyplot(fig)

        st.write("Rata-rata penyewaan sepeda oleh pengguna casual dan registered:")
        st.write(user_type_df)

    # Penyewaan Berdasarkan Jam (hourly analysis)
    elif option == "Penyewaan Berdasarkan Jam":
        st.header("⏰ Penyewaan Berdasarkan Jam")

        # Mengelompokkan data hourly berdasarkan jam untuk analisis penyewaan
        avg_rentals_hourly = df_hour_cleaned.groupby('hr')['cnt'].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x='hr', y='cnt', data=avg_rentals_hourly, marker="o", ax=ax)
        ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Jam', fontsize=16)
        ax.set_xlabel('Jam', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
        st.pyplot(fig)

        st.write("Rata-rata penyewaan sepeda berdasarkan jam:")
        st.write(avg_rentals_hourly)

    # Penyewaan Berdasarkan Musim
    elif option == "Penyewaan Berdasarkan Musim":
        st.header("🌸 Penyewaan Berdasarkan Musim")

        # Mengelompokkan data berdasarkan musim (season) dan menghitung rata-rata penyewaan
        avg_rentals_season = df_day_cleaned.groupby('season')['cnt'].mean().reset_index()

        # Definisikan label musim
        season_labels = {
            1: "Musim Semi",
            2: "Musim Panas",
            3: "Musim Gugur",
            4: "Musim Dingin"
        }
        avg_rentals_season['season'] = avg_rentals_season['season'].map(season_labels)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x='season', y='cnt', data=avg_rentals_season, palette='coolwarm', ax=ax)
        ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Musim', fontsize=16)
        ax.set_xlabel('Musim', fontsize=12)
        ax.set_ylabel('Jumlah Penyewaan Rata-rata', fontsize=12)
        st.pyplot(fig)

        st.write("Rata-rata penyewaan sepeda berdasarkan musim:")
        st.write(avg_rentals_season)

# Jika tidak ada data yang di-load
else:
    st.error("Data tidak tersedia. Harap pastikan file data ada di folder 'Bike-sharing-dataset'.")
