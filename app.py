# Import library
import pandas as pd
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Konfigurasi Layout
st.set_page_config(
    page_title="Dashboard Berita Pilkada",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tambahkan logo di sidebar
st.sidebar.image("logo.png", use_container_width=True)  # Ganti "logo.png" dengan path file logo Anda
st.sidebar.header("⚙️ Filter Data")

# Judul Dashboard
st.title("📊 Dashboard Berita Pilkada Jawa Tengah")
st.markdown("Selamat datang di dashboard analisis berita Pilkada Jawa Tengah. Jelajahi data berdasarkan tahun, kategori, distribusi waktu, dan lainnya.")

# Load Data
@st.cache_data
def load_data():
    # Load file CSV
    data = pd.read_csv("pilkada_jawa_tengah.csv")
    
    # Mapping bulan dan hari dari bahasa Indonesia ke bahasa Inggris
    bulan_mapping = {
        'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Apr', 'Mei': 'May',
        'Jun': 'Jun', 'Jul': 'Jul', 'Agu': 'Aug', 'Sep': 'Sep', 'Okt': 'Oct',
        'Nov': 'Nov', 'Des': 'Dec'
    }
    hari_mapping = {
        'Senin': 'Mon', 'Selasa': 'Tue', 'Rabu': 'Wed', 'Kamis': 'Thu',
        'Jumat': 'Fri', 'Sabtu': 'Sat', 'Minggu': 'Sun'
    }

    # Ganti nama bulan dan hari
    for indo, eng in bulan_mapping.items():
        data['Tanggal'] = data['Tanggal'].str.replace(indo, eng, regex=False)
    for indo, eng in hari_mapping.items():
        data['Tanggal'] = data['Tanggal'].str.replace(indo, eng, regex=False)

    # Konversi kolom Tanggal ke datetime
    data['Tanggal'] = pd.to_datetime(data['Tanggal'], format='%a, %d %b %Y %H:%M WIB', errors='coerce')
    
    # Hapus baris dengan NaT di kolom Tanggal
    data = data.dropna(subset=['Tanggal'])
    # Tambahkan kolom Tahun dan Bulan
    data['Tahun'] = data['Tanggal'].dt.year
    data['Bulan'] = data['Tanggal'].dt.month
    return data

# Panggil fungsi untuk load data
data = load_data()

# Cek jika data kosong setelah konversi
if data.empty:
    st.error("❌ Data tidak tersedia. Periksa format tanggal di file CSV Anda.")
else:
    # Sidebar untuk Filter Tahun
    tahun_unik = sorted(data['Tahun'].dropna().unique())
    selected_tahun = st.sidebar.selectbox("Pilih Tahun", tahun_unik)

    # Filter data berdasarkan tahun
    filtered_data = data[data['Tahun'] == selected_tahun]

    # Tampilkan Data
    st.markdown(f"### 🗓️ Data Berita Pilkada Tahun {selected_tahun}")
    st.dataframe(filtered_data[['Tanggal', 'Judul', 'Deskripsi', 'Kategori', 'Link']])

    # Insight 1: Distribusi Jumlah Berita per Bulan
    st.markdown(f"### 📅 Distribusi Jumlah Berita per Bulan (Tahun {selected_tahun})")
    if not filtered_data.empty:
        # Mapping nama bulan
        bulan_mapping_full = {
            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
            7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
        }
        filtered_data['Nama Bulan'] = filtered_data['Bulan'].map(bulan_mapping_full)
        monthly_count = (
            filtered_data['Nama Bulan']
            .value_counts()
            .reindex(bulan_mapping_full.values(), fill_value=0)
        )
        st.bar_chart(monthly_count)
    else:
        st.write("Tidak ada data untuk distribusi per bulan.")

    # Insight 2: Distribusi Berdasarkan Kategori
    st.markdown(f"### 🗂️ Distribusi Berita Berdasarkan Kategori (Tahun {selected_tahun})")
    if not filtered_data.empty:
        category_count = filtered_data['Kategori'].value_counts()
        st.bar_chart(category_count)
    else:
        st.write("Tidak ada data kategori untuk ditampilkan.")

    # Insight 3: Word Cloud dari Judul Berita
    st.markdown(f"### ☁️ Word Cloud dari Judul Berita (Tahun {selected_tahun})")
    all_titles = " ".join(filtered_data['Judul'].dropna())
    if all_titles.strip():
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_titles)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.write("Tidak ada judul berita untuk membuat Word Cloud.")

    # Insight 4: Berita Paling Populer
    st.markdown(f"### 🌟 Berita Paling Populer (Tahun {selected_tahun})")
    if not filtered_data.empty:
        top_news = filtered_data['Judul'].value_counts().head(5)
        st.write("Berita yang paling sering muncul:")
        st.write(top_news)
    else:
        st.write("Tidak ada data berita populer untuk tahun ini.")
