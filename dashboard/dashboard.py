"""Dashboard PM2.5 Beijing — Dicoding Data Analysis project."""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Beijing Air Quality Analytics", page_icon="🌍", layout="wide")
DATA_PATH = Path(__file__).resolve().parent / "air_quality_clean.csv"
COLORS = {"Rendah": "#BFDBFE", "Sedang": "#93C5FD", "Tinggi": "#3B82F6", "Sangat Tinggi": "#1D4ED8"}
PRIMARY_BLUE = "#2563EB"
NEUTRAL_BLUE = "#94A3B8"
HIGHLIGHT_RED = "#DC2626"
LABELS = list(COLORS)

st.markdown("""
<style>
/* Pengaturan layout dashboard */
.block-container {
    padding-top: 2rem;
    max-width: 1350px;
}

/* KPI Cards - mendukung Dark Mode dan Light Mode */
[data-testid="stMetric"] {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.25);
    padding: 15px;
    border-radius: 12px;
}

/* Warna teks mengikuti tema Streamlit */
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: var(--text-color);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Memuat data kualitas udara...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["datetime"])
    df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")
    df["station"] = df["station"].astype(str)
    return df

st.title("Beijing Air Quality Analytics")
st.caption("Analisis PM2.5 pada 12 stasiun pemantauan | 1 Maret 2013 – 28 Februari 2017")
if not DATA_PATH.exists():
    st.error(f"File data tidak ditemukan: {DATA_PATH.name}. Letakkan CSV di folder dashboard/.")
    st.stop()

df = load_data(str(DATA_PATH))
min_date, max_date = df["datetime"].min().date(), df["datetime"].max().date()

with st.sidebar:
    st.header("Filter Analisis")
    selected_stations = st.multiselect("Stasiun pemantauan", sorted(df["station"].unique()), default=sorted(df["station"].unique()))
    dates = st.date_input("Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    st.divider()
    st.info("Kategori PM2.5 (0–25, >25–50, >50–100, >100 µg/m³) adalah **batas eksploratif**, bukan AQI/ISPU resmi.")
    st.caption("Setiap baris merepresentasikan satu jam pengamatan pada satu stasiun.")

if not selected_stations:
    st.warning("Pilih minimal satu stasiun untuk menampilkan analisis.")
    st.stop()
if not isinstance(dates, (list, tuple)) or len(dates) != 2:
    st.info("Pilih tanggal mulai dan tanggal akhir.")
    st.stop()
start_date, end_date = dates
if start_date > end_date:
    st.error("Tanggal mulai tidak boleh melewati tanggal akhir.")
    st.stop()

filtered = df.loc[
    df["station"].isin(selected_stations)
    & df["datetime"].dt.date.between(start_date, end_date)
].copy()
valid = filtered.dropna(subset=["PM2.5"]).copy()
if valid.empty:
    st.warning("Tidak ada pengamatan PM2.5 valid untuk filter yang dipilih.")
    st.stop()

valid["category"] = pd.cut(valid["PM2.5"], bins=[0, 25, 50, 100, np.inf], labels=LABELS, include_lowest=True)
completeness = len(valid) / len(filtered) * 100
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rata-rata PM2.5", f"{valid['PM2.5'].mean():.2f} µg/m³")
m2.metric("Stasiun terpilih", f"{valid['station'].nunique()}")
m3.metric("Pengamatan valid", f"{len(valid):,}")
m4.metric("Kelengkapan PM2.5", f"{completeness:.2f}%")

st.caption(f"Periode aktif: {start_date:%d %b %Y} – {end_date:%d %b %Y} | Nilai kosong PM2.5 dikecualikan dari perhitungan rata-rata.")

tab1, tab2, tab3, tab4 = st.tabs([" Tren Waktu", "Antarstasiun", "Kategori PM2.5", "Kualitas Data"])
