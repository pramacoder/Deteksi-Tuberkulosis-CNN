# Plan: Pengembangan Model CNN Deteksi Tuberkulosis (TB) dari Chest X-ray

> **Tujuan**: Membangun model klasifikasi biner (Normal vs TB) berbasis CNN dengan transfer learning, sesuai hasil EDA dan Model Selection (Kelompok E).
> **Output akhir**: Notebook Jupyter (`tb_classification.ipynb`) yang dapat dieksekusi end-to-end oleh AI agent di Claude Code.
> **Dasar keputusan**: CNN dipilih (lihat dokumen Model Selection §3.4 & §4) karena ekstraksi fitur otomatis, dukungan transfer learning, dan kemampuan generalisasi terhadap domain shift antar dataset Mendeley & Kaggle.

---

## Struktur Notebook (Modular)

Notebook dibagi menjadi **section bernomor** dengan markdown header (`## 1. ...`, `## 2. ...`, dst.) agar setiap bagian dapat dicari, dijalankan, dan diedit ulang secara independen tanpa merusak section lain. Setiap section diakhiri dengan `print()`/`display()` ringkasan output sebagai checkpoint verifikasi.

```
tb_classification.ipynb
├── 1. Setup & Konfigurasi
├── 2. Data Acquisition & Loading
├── 3. Exploratory Sanity Check (ringkas, EDA detail sudah ada di tugas sebelumnya)
├── 4. Preprocessing & Penyeragaman Data
├── 5. Data Splitting (Train/Val/Test)
├── 6. Data Augmentation Pipeline
├── 7. Model Architecture (CNN + Transfer Learning)
├── 8. Training
├── 9. Evaluation
├── 10. Error Analysis & Domain Shift Check
└── 11. Model Export & Kesimpulan
```

---

## 1. Setup & Konfigurasi

**Tujuan**: Menyiapkan environment dan konstanta global yang dipakai di seluruh notebook.

- [ ] Import library inti: `tensorflow`/`keras`, `numpy`, `pandas`, `matplotlib`, `seaborn`, `sklearn`, `pathlib`, `os`, `cv2` atau `PIL`
- [ ] Set random seed global (numpy, tensorflow, python random) untuk reproducibility
- [ ] Definisikan konstanta konfigurasi di satu cell terpisah (mudah diubah ulang):
  - `IMG_SIZE = (224, 224)` (target resize, kompatibel dengan banyak arsitektur transfer learning)
  - `BATCH_SIZE = 32`
  - `EPOCHS = 30`
  - `RANDOM_SEED = 42`
  - `BASE_DIR`, `DATA_DIR`, `OUTPUT_DIR` (path)
- [ ] Cek ketersediaan GPU (`tf.config.list_physical_devices('GPU')`)

**Checkpoint**: print versi library + status GPU.

---

## 2. Data Acquisition & Loading

**Tujuan**: Memuat dan menggabungkan dataset Mendeley dan Kaggle sesuai deskripsi EDA.

- [ ] Unduh/lokasikan dua sumber dataset:
  - Mendeley: *Dataset of Tuberculosis Chest X-rays Images* (2.494 TB, 514 Normal)
  - Kaggle: *Tuberculosis (TB) Chest X-ray Database* (700 TB, 3.500 Normal) — link: `tawsifurrahman/tuberculosis-tb-chest-xray-dataset`
- [ ] Susun struktur folder gabungan:
  ```
  data/
  ├── raw/
  │   ├── mendeley/{Normal,Tuberculosis}/
  │   └── kaggle/{Normal,Tuberculosis}/
  └── processed/   # diisi pada section 4
  ```
- [ ] Buat dataframe metadata berisi kolom: `filepath`, `label` (Normal/TB), `source` (mendeley/kaggle), `format`, `width`, `height`
- [ ] Validasi jumlah file sesuai EDA: total 7.208 (3.194 TB, 4.014 Normal)

**Checkpoint**: `df.groupby(['source','label']).size()` harus cocok dengan tabel EDA.

---

## 3. Exploratory Sanity Check (Ringkas)

**Tujuan**: Verifikasi cepat sebelum preprocessing — EDA mendalam sudah dilakukan di tugas Kelompok 3, jadi cukup sanity check.

- [ ] Tampilkan beberapa sampel gambar per kelas per sumber (grid 2x4)
- [ ] Cek ulang distribusi kelas (bar chart) → konfirmasi rasio ~1:1.26
- [ ] Cek ulang distribusi resolusi & format antar sumber (Mendeley ~255x250 JPG vs Kaggle 512x512 PNG)
- [ ] Deteksi gambar corrupt/blur dengan Laplacian variance (threshold < 50), buat list file kandidat untuk dikecualikan

**Checkpoint**: ringkasan tabel jumlah gambar valid vs dikecualikan.

---

## 4. Preprocessing & Penyeragaman Data

**Tujuan**: Menyamakan resolusi, format, dan skala piksel sesuai rekomendasi EDA §D.4.

- [ ] **Resize**: semua gambar → `IMG_SIZE = (224, 224)`, interpolasi bilinear, jaga aspect ratio dengan padding jika perlu
- [ ] **Konversi format**: standarkan ke 1 format (misal PNG) saat menyimpan ke `data/processed/`
- [ ] **Color mode**: tentukan grayscale vs RGB (jika pakai transfer learning ImageNet → konversi grayscale ke 3-channel RGB)
- [ ] **Normalisasi**: skala piksel ke `[0,1]` (rescale 1/255) atau preprocessing khusus arsitektur (misal `preprocess_input` untuk EfficientNet/ResNet)
- [ ] Buang/lewati file corrupt/blur hasil section 3
- [ ] Simpan dataframe metadata final (`metadata_clean.csv`) dengan kolom path baru ke `data/processed/`

**Checkpoint**: tampilkan histogram ukuran gambar setelah resize (harus seragam 224x224) dan distribusi nilai piksel setelah normalisasi.

---

## 5. Data Splitting (Train/Val/Test)

**Tujuan**: Membagi data secara stratified agar distribusi kelas & sumber tetap proporsional.

- [ ] Split: **70% train / 15% validation / 15% test**, `stratify` berdasarkan kombinasi `label` (dan idealnya `source` agar domain shift terwakili di semua split)
- [ ] Gunakan `train_test_split` dari sklearn dua tahap (train+val vs test, lalu train vs val)
- [ ] Pastikan **tidak ada data leakage**: split dilakukan di level file sebelum augmentasi
- [ ] Simpan daftar split ke CSV (`train.csv`, `val.csv`, `test.csv`) untuk reproducibility
- [ ] Cetak tabel kontingensi `label x source` untuk masing-masing split

**Checkpoint**: tabel ringkasan jumlah sampel per split per kelas per sumber.

---

## 6. Data Augmentation Pipeline

**Tujuan**: Mengurangi overfitting & memperkuat generalisasi, sesuai EDA §B.5/§D.2 — hanya augmentasi yang aman secara anatomis.

- [ ] Augmentasi **hanya pada training set**, via `tf.keras.Sequential` augmentation layers atau `ImageDataGenerator`:
  - Horizontal flip
  - Rotasi kecil (±10–15°)
  - Brightness adjustment (±10–20%)
  - Contrast adjustment
- [ ] **Hindari**: vertical flip, shear ekstrem, zoom berlebihan (dapat mengubah struktur anatomi)
- [ ] Bangun `tf.data.Dataset` pipeline:
  - `train_ds`: load → resize (jika belum) → augment → batch → prefetch
  - `val_ds`, `test_ds`: load → resize → batch → prefetch (tanpa augmentasi)
- [ ] Visualisasi: tampilkan 1 gambar asli + 5 versi augmentasinya

**Checkpoint**: grid visualisasi augmentasi + cek shape batch (`(BATCH_SIZE, 224, 224, 3)`).

---

## 7. Model Architecture (CNN + Transfer Learning)

**Tujuan**: Bangun model sesuai keputusan Model Selection — CNN dengan transfer learning untuk mengatasi domain shift.

- [ ] **Base model**: gunakan pretrained CNN (pilih salah satu, beri opsi untuk dibandingkan):
  - `EfficientNetB0` (efisien, akurat)
  - `ResNet50` (baseline kuat, banyak dipakai literatur medis)
  - `VGG16` (sering jadi baseline pada paper TB chest X-ray)
- [ ] Load pretrained weights `imagenet`, `include_top=False`
- [ ] **Strategi fine-tuning bertahap**:
  1. Tahap awal: freeze base model, latih hanya head (classifier baru)
  2. Tahap lanjut (opsional): unfreeze beberapa layer atas base model, fine-tune dengan learning rate kecil
- [ ] **Head classifier**:
  - `GlobalAveragePooling2D`
  - `Dense(128, activation='relu')` + `Dropout(0.3–0.5)`
  - `Dense(1, activation='sigmoid')` (binary classification)
- [ ] Compile: `optimizer=Adam(lr=1e-4)`, `loss='binary_crossentropy'`, `metrics=['accuracy', AUC, Precision, Recall]`
- [ ] Tampilkan `model.summary()` dan jumlah parameter trainable vs total

**Checkpoint**: summary model + diagram arsitektur (`tf.keras.utils.plot_model`, opsional).

---

## 8. Training

**Tujuan**: Melatih model dengan callback yang sesuai dan mempertimbangkan ketidakseimbangan kelas ringan (1:1.26).

- [ ] **Class weighting (opsional)**: hitung `class_weight` dengan `sklearn.utils.class_weight.compute_class_weight` — sesuai EDA, rasio ringan jadi tidak wajib tapi tetap bisa diuji
- [ ] **Callbacks**:
  - `EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)`
  - `ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3)`
  - `ModelCheckpoint(filepath='best_model.keras', monitor='val_auc', save_best_only=True)`
- [ ] **Training tahap 1** (frozen base): `model.fit(train_ds, validation_data=val_ds, epochs=..., callbacks=...)`
- [ ] **Training tahap 2** (fine-tuning, opsional): unfreeze top layers, recompile dengan LR lebih kecil (`1e-5`), lanjutkan training
- [ ] Plot learning curves: `loss` & `accuracy`/`AUC` untuk train vs val per epoch

**Checkpoint**: grafik training history (2 subplot: loss, AUC) tahap 1 dan tahap 2.

---

## 9. Evaluation

**Tujuan**: Evaluasi performa model pada test set secara menyeluruh, selaras dengan tujuan klinis (skrining awal TB).

- [ ] Evaluasi pada `test_ds`: `accuracy`, `precision`, `recall`, `F1-score`, `AUC-ROC`
- [ ] **Confusion matrix** (heatmap)
- [ ] **ROC curve** dan **Precision-Recall curve**
- [ ] Tentukan threshold klasifikasi optimal (selain default 0.5), pertimbangkan **recall tinggi untuk kelas TB** (minimisasi false negative, krusial untuk skrining medis)
- [ ] Tabel ringkasan metrik (markdown table) untuk dokumentasi

**Checkpoint**: tabel metrik final + confusion matrix + ROC-AUC.

---

## 10. Error Analysis & Domain Shift Check

**Tujuan**: Memastikan model tidak mengandalkan spurious correlation antar sumber dataset (sesuai temuan EDA §C.4).

- [ ] Breakdown metrik evaluasi **per sumber dataset** (Mendeley vs Kaggle) — cek apakah ada gap performa signifikan
- [ ] Visualisasi **misclassified samples** (false positive & false negative) — tampilkan gambar + label asli + prediksi + confidence
- [ ] (Opsional, jika waktu memungkinkan) Grad-CAM/saliency map untuk beberapa sampel benar & salah klasifikasi — cek apakah model fokus pada area paru, bukan artefak (marker lateralitas, dll.)
- [ ] Catat temuan domain shift: apakah model lebih akurat di salah satu sumber

**Checkpoint**: tabel metrik per sumber + grid contoh misklasifikasi.

---

## 11. Model Export & Kesimpulan

**Tujuan**: Menyimpan artefak final dan menulis kesimpulan ringkas.

- [ ] Simpan model final: `model.save('outputs/tb_cnn_model.keras')`
- [ ] Simpan riwayat training (`history.history` → CSV/JSON)
- [ ] Simpan metrik evaluasi final ke `outputs/evaluation_report.json`
- [ ] Tulis cell markdown kesimpulan: ringkasan performa, perbandingan dengan ekspektasi dari tugas Model Selection, batasan model, dan rekomendasi langkah selanjutnya (misal: hyperparameter tuning, ensemble, eksplorasi arsitektur lain)

**Checkpoint**: daftar file output di direktori `outputs/`.

---

## Catatan untuk Eksekusi oleh AI Agent (Claude Code)

- Setiap section di atas sebaiknya **satu atau lebih cell terpisah** dalam notebook, dengan header markdown identik dengan judul section ini agar mudah dicari (`Ctrl+F` pada judul section).
- Jalankan section secara berurutan; setiap section memiliki "Checkpoint" yang harus tampil sebelum lanjut ke section berikutnya — gunakan ini sebagai sinyal validasi otomatis.
- Konstanta di Section 1 (`IMG_SIZE`, `BATCH_SIZE`, dll.) adalah satu-satunya tempat yang perlu diubah jika ingin eksperimen ulang skala kecil — section lain tidak perlu di-hardcode ulang.
- Jika dataset belum tersedia secara lokal, Section 2 perlu disesuaikan dengan mekanisme download (`kagglehub` atau API Kaggle untuk dataset Kaggle; download manual/link untuk Mendeley).
- Section 7–8 dirancang agar arsitektur (`EfficientNetB0`/`ResNet50`/`VGG16`) bisa ditukar dengan mengubah satu baris konfigurasi tanpa mengubah pipeline lain.
