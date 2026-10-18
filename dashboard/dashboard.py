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

with tab1:
    st.subheader("Tren rata-rata PM2.5")
    st.caption("Tahun 2013 dan 2017 merupakan tahun parsial pada dataset asli; filter tanggal juga dapat menghasilkan periode parsial.")
    yearly = valid.groupby(valid["datetime"].dt.year)["PM2.5"].agg(["mean", "count"]).reset_index().rename(columns={"datetime": "Tahun", "mean": "Rata-rata PM2.5", "count": "Pengamatan valid"})
    fig = px.line(yearly, x="Tahun", y="Rata-rata PM2.5", markers=True, text=yearly["Rata-rata PM2.5"].round(2), color_discrete_sequence=[PRIMARY_BLUE])
    fig.update_traces(textposition="top center")
    fig.update_layout(yaxis_title="Rata-rata PM2.5 (µg/m³)", xaxis=dict(dtick=1), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(yearly.round(2), hide_index=True, use_container_width=True)
    st.subheader("Fluktuasi bulanan")
    monthly = valid.groupby(valid["datetime"].dt.to_period("M"))["PM2.5"].mean().reset_index()
    monthly.columns = ["Bulan", "Rata-rata PM2.5"]
    monthly["Bulan"] = monthly["Bulan"].dt.to_timestamp()
    fig_month = px.line(monthly, x="Bulan", y="Rata-rata PM2.5", markers=True, color_discrete_sequence=[PRIMARY_BLUE])
    fig_month.update_layout(yaxis_title="Rata-rata PM2.5 (µg/m³)", xaxis_title="Bulan")
    st.plotly_chart(fig_month, use_container_width=True)
    complete_years = yearly[yearly["Tahun"].between(2014, 2016)]
    if len(complete_years) == 3 and start_date <= pd.Timestamp("2014-01-01").date() and end_date >= pd.Timestamp("2016-12-31").date():
        peak = complete_years.loc[complete_years["Rata-rata PM2.5"].idxmax()]
        st.success(f"Pada tahun kalender lengkap 2014–2016, rata-rata tertinggi terjadi pada **{int(peak['Tahun'])}** ({peak['Rata-rata PM2.5']:.2f} µg/m³) untuk stasiun yang dipilih.")
    else:
        st.info("Untuk membandingkan tahun kalender lengkap 2014–2016, gunakan rentang tanggal yang mencakup ketiga tahun tersebut.")

with tab2:
    st.subheader("Perbandingan rata-rata PM2.5 antarstasiun")
    by_station = valid.groupby("station")["PM2.5"].agg(["mean", "count"]).reset_index().rename(columns={"mean": "Rata-rata PM2.5", "count": "Pengamatan valid"}).sort_values("Rata-rata PM2.5", ascending=False)
    high_name = by_station.iloc[0]["station"]
    low_name = by_station.iloc[-1]["station"]
    by_station["Penanda"] = np.where(by_station["station"] == high_name, "Tertinggi", "Lainnya")
    fig_station = px.bar(by_station, x="Rata-rata PM2.5", y="station", orientation="h", color="Penanda", color_discrete_map={"Tertinggi": HIGHLIGHT_RED, "Lainnya": NEUTRAL_BLUE}, text=by_station["Rata-rata PM2.5"].round(2))
    fig_station.update_layout(yaxis={"categoryorder": "array", "categoryarray": by_station["station"].iloc[::-1].tolist()}, xaxis_title="Rata-rata PM2.5 (µg/m³)", yaxis_title="Stasiun", xaxis=dict(rangemode="tozero"), legend_title_text="Penekanan visual")
    fig_station.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_station, use_container_width=True)
    st.caption("**Makna warna:** merah menyoroti stasiun dengan rata-rata PM2.5 tertinggi pada filter aktif; abu-abu kebiruan menunjukkan stasiun lainnya. Semua batang dimulai dari nol.")
    if len(by_station) > 1:
        gap = by_station.iloc[0]["Rata-rata PM2.5"] - by_station.iloc[-1]["Rata-rata PM2.5"]
        st.info(f"**Tertinggi:** {high_name} ({by_station.iloc[0]['Rata-rata PM2.5']:.2f} µg/m³). **Terendah:** {low_name} ({by_station.iloc[-1]['Rata-rata PM2.5']:.2f} µg/m³). **Selisih:** {gap:.2f} µg/m³.")
    st.dataframe(by_station.drop(columns="Penanda").round(2), hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Distribusi kategori konsentrasi PM2.5")
    category_count = valid["category"].value_counts(sort=False).reindex(LABELS, fill_value=0).rename_axis("Kategori").reset_index(name="Jumlah")
    category_count["Persentase"] = category_count["Jumlah"] / len(valid) * 100
    fig_cat = px.bar(category_count, x="Kategori", y="Persentase", color="Kategori", color_discrete_map=COLORS, text=category_count["Persentase"].map(lambda x: f"{x:.1f}%"))
    fig_cat.update_layout(yaxis_title="Persentase pengamatan valid (%)", showlegend=False, yaxis=dict(rangemode="tozero"))
    st.plotly_chart(fig_cat, use_container_width=True)
    st.caption("Gradasi biru muda → biru tua menunjukkan interval konsentrasi PM2.5 yang semakin tinggi, **bukan** tingkat AQI/ISPU resmi. Persentase berdasarkan pengamatan PM2.5 valid.")
    st.dataframe(category_count.round(2), hide_index=True, use_container_width=True)
    st.subheader("Komposisi kategori per stasiun")
    counts = pd.crosstab(valid["station"], valid["category"]).reindex(columns=LABELS, fill_value=0)
    shares = counts.div(counts.sum(axis=1), axis=0).mul(100)
    shares["Proporsi >50"] = shares["Tinggi"] + shares["Sangat Tinggi"]
    shares = shares.sort_values("Proporsi >50", ascending=False)
    plot_data = shares[LABELS].reset_index().melt(id_vars="station", var_name="Kategori", value_name="Persentase")
    fig_stack = px.bar(plot_data, x="Persentase", y="station", color="Kategori", orientation="h", category_orders={"station": shares.index.tolist()[::-1], "Kategori": LABELS}, color_discrete_map=COLORS)
    fig_stack.update_layout(barmode="stack", xaxis=dict(range=[0, 100]), xaxis_title="Persentase pengamatan valid (%)", yaxis_title="Stasiun", legend_title_text="Interval PM2.5")
    st.plotly_chart(fig_stack, use_container_width=True)
    st.caption("Kategori bersifat eksploratif; warna konsisten dengan grafik distribusi kategori. Persentase dihitung dari pengamatan PM2.5 valid per stasiun.")

with tab4:
    st.subheader("Kelengkapan data PM2.5")
    completeness_station = filtered.groupby("station")["PM2.5"].agg(total="size", valid="count").reset_index()
    completeness_station["Hilang"] = completeness_station["total"] - completeness_station["valid"]
    completeness_station["Kelengkapan (%)"] = completeness_station["valid"] / completeness_station["total"] * 100
    st.dataframe(completeness_station.round(2), hide_index=True, use_container_width=True)
    fig_complete = px.bar(completeness_station.sort_values("Kelengkapan (%)"), x="Kelengkapan (%)", y="station", orientation="h", color_discrete_sequence=[PRIMARY_BLUE], range_x=[0, 100])
    fig_complete.update_layout(yaxis_title="Stasiun")
    st.plotly_chart(fig_complete, use_container_width=True)
    st.caption("Pengamatan yang hilang dapat memengaruhi perbandingan. Dashboard tidak melakukan imputasi atau menghapus outlier PM2.5.")

st.divider()
st.caption("Sumber: Beijing Multi-Site Air Quality Dataset (2013–2017). Analisis bersifat deskriptif; tidak mengidentifikasi penyebab polusi atau risiko kesehatan individu.")
