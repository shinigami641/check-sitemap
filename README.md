# Sitemap Scanner - Web Vulnerability Detector

## Ringkasan Project
Project ini bertujuan untuk memetakan sitemap sebuah website dengan metode scraping data, kemudian menganalisis endpoint yang ditemukan untuk mencari potensi kelemahan SQL Injection (SQLi). Tool ini dapat digunakan sebagai bagian dari proses penetration testing untuk mengidentifikasi celah keamanan pada aplikasi web.

## Metode Pemetaan Sitemap
Beberapa metode yang digunakan dalam project ini:

1. **Scraping XML Sitemap** - Mengambil dan mengurai file sitemap.xml yang tersedia pada banyak website
2. **Crawling Web** - Menjelajahi website secara otomatis dan mengikuti semua link yang ditemukan
3. **Parsing Robots.txt** - Menganalisis file robots.txt untuk menemukan direktori dan endpoint yang tersembunyi
4. **Brute Force Directory** - Mencoba kombinasi path umum untuk menemukan endpoint yang tidak terdokumentasi

## Fitur Utama
- Ekstraksi dan parsing sitemap.xml
- Crawling website untuk menemukan endpoint
- Deteksi parameter URL yang rentan terhadap SQLi
- Pengujian otomatis untuk kerentanan SQLi dasar
- Pelaporan hasil dalam format yang mudah dibaca

## Milestone Project

### Tahap 1: Inisiasi (Saat Ini)
- [x] Setup struktur project dasar
- [ ] Implementasi fungsi scraping sitemap.xml
- [ ] Implementasi fungsi parsing robots.txt
- [ ] Implementasi fungsi crawling dasar

### Tahap 2: Pengembangan Fitur Utama
- [ ] Implementasi deteksi parameter URL
- [ ] Pengembangan modul pengujian SQLi
- [ ] Integrasi dengan database untuk menyimpan hasil

### Tahap 3: Pengujian dan Optimasi
- [ ] Pengujian pada berbagai jenis website
- [ ] Optimasi performa dan penanganan error
- [ ] Implementasi fitur threading untuk mempercepat proses

### Tahap 4: Pelaporan dan Visualisasi
- [ ] Pengembangan format laporan yang komprehensif
- [ ] Implementasi visualisasi hasil (grafik, diagram)
- [ ] Integrasi dengan tools keamanan lainnya

## Tujuan Project
Project ini dikembangkan untuk membantu security researcher dan penetration tester dalam:
1. Memetakan struktur website secara otomatis
2. Mengidentifikasi endpoint yang berpotensi rentan terhadap serangan SQLi
3. Melakukan pengujian awal untuk memverifikasi kerentanan
4. Menghasilkan laporan yang dapat digunakan untuk perbaikan keamanan

## Penggunaan
Instruksi penggunaan akan ditambahkan setelah implementasi fitur dasar selesai.

## Kontribusi
Kontribusi untuk pengembangan project ini sangat diterima. Silakan fork repository ini dan kirimkan pull request Anda.

## Disclaimer
Tool ini hanya boleh digunakan untuk tujuan pengujian keamanan yang sah dan etis. Penggunaan untuk aktivitas ilegal dilarang keras.