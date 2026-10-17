# Beijing Air Quality Analytics Dashboard

Dashboard interaktif untuk eksplorasi PM2.5 pada 12 stasiun pemantauan Beijing (1 Maret 2013 – 28 Februari 2017).

## Fitur

- Filter tanggal dan satu/multi-stasiun
- Ringkasan rata-rata PM2.5, jumlah pengamatan valid, dan kelengkapan data
- Tren tahunan dan bulanan
- Peringkat rata-rata PM2.5 antarstasiun beserta selisih tertinggi–terendah
- Binning eksploratif PM2.5 dan 100% stacked bar chart
- Pemeriksaan kelengkapan PM2.5 per stasiun

## Menjalankan di lokal

1. Buka terminal di folder ini.
2. Buat virtual environment (opsional): `python -m venv .venv`.
3. Aktifkan environment sesuai sistem operasi.
4. Jalankan `pip install -r requirements.txt`.
5. Jalankan `streamlit run dashboard/dashboard.py`.
6. Buka alamat localhost yang ditampilkan Streamlit.

## Deployment Streamlit Community Cloud

1. Upload folder proyek ke repositori GitHub milik Anda.
2. Pastikan `dashboard/dashboard.py`, `dashboard/air_quality_clean.csv`, dan `requirements.txt` ikut terunggah.
3. Di Streamlit Community Cloud, pilih repositori, branch, dan entrypoint `dashboard/dashboard.py`.
4. Deploy; setelah berhasil, salin URL aplikasi ke `url.txt` untuk submission bila diperlukan.

## Metodologi

Dataset digabung dari 12 CSV sumber; `datetime` dibentuk dari `year`, `month`, `day`, dan `hour`. Pengamatan PM2.5 kosong dikecualikan dari perhitungan PM2.5, tetapi tetap dihitung untuk metrik kelengkapan. Outlier tidak dihapus. Binning (0–25, >25–50, >50–100, >100 µg/m³) hanya kategori eksploratif, bukan AQI/ISPU resmi. Rata-rata tahunan menggunakan semua pengamatan valid dalam periode dan stasiun terpilih; periode parsial perlu diinterpretasi secara hati-hati.

## Data

Sumber: Beijing Multi-Site Air Quality Dataset. Dataset mentah disertakan sebagai `data/Air-quality-dataset.zip`. Data bersih berada di `dashboard/air_quality_clean.csv`.

## Catatan submission

`Proyek_Analisis_Data.ipynb` di paket ini adalah **template awal yang diunggah**, bukan notebook analisis final yang telah dieksekusi. Ganti dengan notebook final Anda yang sudah berisi kode, Markdown, dan output seluruh tahap sebelum mengumpulkan submission.

## 🌐 Live Dashboard

Dashboard Beijing Air Quality Analytics telah
di-deploy menggunakan Streamlit Community Cloud.

Akses dashboard melalui:

https://beijing-air-quality-analyticsgit-nsddpcnv3jcydewphplvdq.streamlit.app/

## 📊 Dashboard Features

- Interactive PM2.5 monitoring dashboard
- Annual and monthly PM2.5 trends
- Air quality comparison across 12 monitoring stations
- PM2.5 concentration categorization
- Data completeness analysis
- Interactive station and date filters
