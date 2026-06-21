# Perbedaan Karakteristik Dataset: Mendeley vs Kaggle

> **Tujuan dokumen**: Menjelaskan perbedaan mendasar antara dua sumber data (Mendeley & Kaggle) berdasarkan hasil EDA dan Model Selection, serta menegaskan bagian pipeline mana yang **tidak boleh** memperlakukan kedua dataset secara seragam (treat-as-one) oleh AI agent saat implementasi notebook.
>
> Dokumen ini bersifat **referensi pendamping** untuk `plan.md` — dibaca sebelum mengeksekusi Section 2, 4, 5, 6, dan 10.

---

## 1. Ringkasan Perbedaan Sumber Data

| Aspek | Mendeley | Kaggle |
|---|---|---|
| Total gambar | 3.008 (514 Normal, 2.494 TB) | 4.200 (3.500 Normal, 700 TB) |
| Distribusi kelas | Didominasi **TB** (~83%) | Didominasi **Normal** (~83%) |
| Sumber institusi | 1 rumah sakit lokal (Pakistan) | Gabungan 4 repository internasional (NLM, Belarus TB Portal, NIAID, RSNA) |
| Resolusi gambar | Bervariasi, mayoritas ~255×250 px | Seragam 512×512 px |
| Format file | JPG | PNG |
| Preprocessing awal | Sudah melalui standarisasi dasar | Tidak dijelaskan, tapi seragam secara teknis |
| Variasi internal | Relatif homogen (1 sumber) | Heterogen (4 sub-sumber dengan karakteristik berbeda-beda) |
| Kualitas/ketajaman | Tidak ada catatan blur signifikan | Ditemukan gambar TB dari Belarus TB Portal dengan ketajaman sangat rendah (Laplacian variance rendah) |

---

## 2. Mengapa Kedua Dataset TIDAK Boleh Diperlakukan Sama

### 2.1 Distribusi Kelas yang Berlawanan
Mendeley didominasi TB, Kaggle didominasi Normal. Jika digabung **tanpa stratifikasi berdasarkan sumber**, ada risiko:
- Split train/val/test menjadi tidak proporsional — misalnya mayoritas sampel TB di test set kebetulan berasal dari satu sumber saja.
- Model "belajar shortcut": mengasosiasikan karakteristik visual sumber (bukan fitur klinis TB) dengan label kelas, karena label dan sumber **berkorelasi kuat** sebelum digabung.

**Implikasi untuk agent**: Section 5 (`Data Splitting`) wajib melakukan stratifikasi **dua dimensi** — `label` DAN `source` — bukan hanya `label`. Gunakan kolom gabungan, misal `strat_key = label + "_" + source`, sebagai argumen `stratify`.

### 2.2 Resolusi dan Format Berbeda
Mendeley (~255×250, JPG) vs Kaggle (512×512, PNG) memiliki resolusi native yang sangat berbeda.

**Risiko jika diperlakukan sama**: Resize naif ke ukuran target (misal 224×224) tanpa memperhatikan rasio downscale yang berbeda dapat menghasilkan **artefak interpolasi yang berbeda secara sistematis** antar sumber — gambar Mendeley di-*upscale* (255→224 relatif kecil downscale), sedangkan Kaggle di-*downscale* signifikan (512→224). Perbedaan artefak ini bisa menjadi sinyal domain shift tambahan yang dipelajari model secara tidak sengaja.

**Implikasi untuk agent**: Section 4 (`Preprocessing`) sebaiknya:
- Mencatat resolusi asli sebagai metadata sebelum resize (sudah ada di kolom `width`/`height` pada Section 2).
- Menggunakan metode interpolasi yang konsisten (misal `INTER_AREA` untuk downscale, `INTER_LINEAR` untuk upscale) — bukan satu metode default untuk semua.
- Pertimbangkan analisis tambahan di Section 10: apakah error model berkorelasi dengan resolusi asli gambar.

### 2.3 Komposisi Internal yang Berbeda (Sub-sumber)
Kaggle bukan dataset tunggal — ia gabungan 4 sub-sumber (NLM, Belarus, NIAID, RSNA) dengan karakteristik teknis berbeda-beda, sedangkan Mendeley berasal dari 1 institusi tunggal.

**Risiko jika diperlakukan sama**: Variasi intra-kelas pada Kaggle jauh lebih tinggi daripada Mendeley. Jika augmentasi atau bobot kelas dihitung berdasarkan asumsi homogenitas, model bisa under-fit terhadap sub-sumber minoritas Kaggle (misal NIAID hanya kontribusi sebagian dari 700 gambar TB Kaggle).

**Implikasi untuk agent**:
- Jika metadata sub-sumber (NLM/Belarus/NIAID/RSNA) tersedia di dataset Kaggle, **simpan sebagai kolom tambahan** (`sub_source`) di Section 2 — jangan hanya `source = "kaggle"`.
- Section 10 (`Error Analysis`) idealnya breakdown bukan hanya per `source` (Mendeley vs Kaggle) tapi juga per `sub_source` jika memungkinkan, untuk mendeteksi sub-populasi yang berperforma buruk.

### 2.4 Kualitas Gambar Tidak Seragam (Blur/Corrupt)
Temuan EDA: beberapa gambar TB dari **Belarus TB Portal** (bagian dari Kaggle) memiliki Laplacian variance sangat rendah (indikasi blur), sedangkan tidak ada catatan serupa untuk Mendeley.

**Risiko jika diperlakukan sama**: Filter kualitas (threshold Laplacian variance < 50) yang diterapkan secara global mungkin **lebih banyak membuang sampel TB dari Kaggle/Belarus** dibandingkan dari Mendeley — ini bisa memperburuk lagi ketidakseimbangan kelas TB pada Kaggle (yang sudah minoritas, 700 gambar).

**Implikasi untuk agent**: Section 3 (`Sanity Check`) — saat membuang gambar blur, **laporkan jumlah yang dibuang per source/sub_source**, bukan hanya total agregat. Jika pembuangan signifikan timpang ke satu sumber, pertimbangkan apakah perlu penyesuaian (misal threshold lebih longgar untuk sub-sumber tertentu, atau dokumentasikan dampaknya pada Section 11).

### 2.5 Label "Normal" Tidak Homogen Secara Klinis
Sebagian besar label "Normal" pada Kaggle berasal dari RSNA Pneumonia Challenge — artinya pasien bebas pneumonia, **bukan eksplisit "paru sehat sempurna"**. Sementara label "Normal" Mendeley berasal dari satu klinik dengan standar lokal.

**Risiko jika diperlakukan sama**: Ini bukan label error (sudah dijustifikasi valid di EDA §C.3), tapi tetap merupakan **sumber variasi intra-kelas Normal** yang berbeda antar sumber. Augmentasi atau class weighting yang dihitung tanpa kesadaran ini tidak akan jadi masalah besar (rasio ringan 1:1.26), tapi error analysis tetap perlu membedakannya.

**Implikasi untuk agent**: Section 10 — saat menampilkan misclassified samples kelas Normal, cek apakah false positive (Normal diprediksi TB) terkonsentrasi pada sampel Normal dari RSNA (kemungkinan ada kondisi paru non-TB lain yang menyerupai TB secara visual).

### 2.6 Domain Shift Sebagai Fitur, Bukan Noise yang Dihilangkan
EDA menegaskan adanya domain shift (perbedaan perangkat, protokol akuisisi, populasi pasien) antar Mendeley dan Kaggle. Model Selection menjustifikasi **transfer learning** sebagai solusi karena domain shift tidak bisa "dihilangkan" lewat preprocessing biasa.

**Risiko jika diperlakukan sama**: Jika notebook hanya melaporkan metrik agregat (akurasi/AUC keseluruhan test set) tanpa breakdown per sumber, model yang sebenarnya **overfit ke karakteristik satu sumber** bisa tampak baik secara agregat tapi gagal generalisasi ke sumber lain (atau data dunia nyata).

**Implikasi untuk agent**: Section 9 (`Evaluation`) wajib disertai Section 10 (`Domain Shift Check`) sebagai langkah **non-opsional**, bukan "opsional jika waktu memungkinkan" — breakdown metrik per `source` adalah bukti utama bahwa model generalisasi lintas domain, sesuai justifikasi pemilihan CNN+transfer learning di Model Selection.

---

## 3. Ringkasan Tindakan Wajib per Section `plan.md`

| Section | Perlakuan Khusus yang Wajib |
|---|---|
| 2. Data Loading | Simpan kolom `source` (dan `sub_source` jika tersedia) per gambar |
| 3. Sanity Check | Laporkan jumlah gambar dibuang (blur/corrupt) **per source** |
| 4. Preprocessing | Metode interpolasi resize disesuaikan arah scaling (up vs down) per source |
| 5. Data Splitting | Stratifikasi berdasarkan `label` × `source` (bukan `label` saja) |
| 6. Augmentation | Augmentasi diterapkan seragam pada training set, tapi distribusi sumber di training set harus tetap representatif (hasil dari stratifikasi Section 5) |
| 9. Evaluation | Tampilkan metrik agregat (test set keseluruhan) |
| 10. Domain Shift Check | **Wajib**: breakdown metrik (akurasi, recall, precision, AUC) per `source`, idealnya juga per `sub_source` untuk Kaggle |

---

## 4. Catatan Tambahan

- Perbedaan-perbedaan di atas **tidak berarti kedua dataset harus dimodelkan secara terpisah** — penggabungan tetap dilakukan (sesuai EDA, untuk menetralkan ketidakseimbangan kelas yang berlawanan). Yang ditekankan adalah: **proses penggabungan dan evaluasi harus sadar terhadap asal data**, bukan menganggap dataset gabungan sebagai satu populasi homogen.
- Jika di kemudian hari ditemukan gap performa besar antar sumber pada Section 10, opsi mitigasi yang bisa dieksplorasi: domain-adversarial training, fine-tuning bertahap per domain, atau augmentasi tambahan yang menyamakan distribusi kontras/kecerahan antar sumber.
