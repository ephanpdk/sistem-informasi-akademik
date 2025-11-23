========================================================================
PANDUAN INSTALASI DAN PENGGUNAAN SISTEM INFORMASI AKADEMIK (SIAK)
========================================================================

Aplikasi ini adalah sistem desktop berbasis Python (PySide6) untuk manajemen 
data akademik (Mahasiswa, Dosen, Matakuliah, Nilai) dengan database PostgreSQL.

DAFTAR FILE:
1. main.py                : File utama aplikasi (GUI).
2. database_models.py     : Konfigurasi koneksi dan skema database (ORM).
3. buat_admin_awal.py     : Script untuk membuat user Admin pertama kali.
4. buat_data_dummy.py     : Script generate data Excel (Dosen/Mhs) untuk di-import.
5. cek_koneksi.py         : Script diagnosa koneksi database.

========================================================================
1. PRASYARAT (SYSTEM REQUIREMENTS)
========================================================================
Pastikan komputer Anda sudah terinstall:
1. Python 3.10 atau versi lebih baru.
2. PostgreSQL (Pastikan service berjalan).
3. pgAdmin (Opsional, untuk memantau database).

========================================================================
2. INSTALASI LIBRARY (DEPENDENCIES)
========================================================================
Buka terminal/CMD di folder proyek ini, lalu jalankan perintah berikut
untuk menginstall semua library yang dibutuhkan:

   pip install PySide6 SQLAlchemy psycopg2-binary pandas openpyxl bcrypt faker

Keterangan Library:
- PySide6: Framework GUI Desktop.
- SQLAlchemy & psycopg2: Koneksi ke PostgreSQL.
- Pandas & openpyxl: Import/Export Excel.
- Bcrypt: Keamanan password.
- Faker: Membuat data dummy.

========================================================================
3. KONFIGURASI DATABASE
========================================================================
Langkah 1: Buat Database Kosong
Buka pgAdmin atau terminal PostgreSQL, lalu buat database baru bernama:
   db_siak_tugas

Langkah 2: Atur Kredensial
Buka file 'database_models.py' dengan text editor. Cari baris:
   DATABASE_URL = "postgresql://postgres:admin@localhost:5432/db_siak_tugas"

Sesuaikan bagian berikut dengan settingan PostgreSQL Anda:
- 'postgres'  -> ganti dengan username database Anda.
- 'admin'     -> ganti dengan password database Anda.
- 'localhost' -> biarkan jika database ada di komputer yang sama.

Langkah 3: Tes Koneksi (Opsional)
Jalankan perintah ini untuk memastikan koneksi berhasil:
   python cek_koneksi.py

========================================================================
4. INISIALISASI DATA AWAL (SETUP)
========================================================================
Sebelum menjalankan aplikasi, kita perlu membuat tabel dan akun admin.

Langkah 1: Buat Tabel dan Admin
Jalankan script berikut. Script ini akan otomatis membuat tabel-tabel di 
database jika belum ada, dan membuat akun admin.
   python buat_admin_awal.py

   Catat akun yang muncul di terminal:
   Username: admin
   Password: admin123

Langkah 2: Generate Data Dummy (Excel)
Aplikasi ini mendukung Import Excel. Jalankan script ini untuk membuat 
file Excel berisi data palsu (Mahasiswa & Dosen) yang siap di-import:
   python buat_data_dummy.py

   Hasil output file (akan muncul di folder proyek):
   - data_dosen_baru.xlsx
   - data_mahasiswa_baru.xlsx
   - data_matakuliah_fix_import.xlsx (jika tersedia)

========================================================================
5. MENJALANKAN APLIKASI
========================================================================
Untuk membuka aplikasi, jalankan perintah:

   python main.py

Jendela Login akan muncul.

========================================================================
6. CARA PENGGUNAAN (ALUR IMPORT & EXPORT)
========================================================================

A. LOGIN
   - Masukkan Username: admin
   - Masukkan Password: admin123
   - Klik Login.

B. IMPORT DATA (Mengisi Database)
   Karena database masih kosong (selain admin), lakukan import data:
   1. Masuk ke menu "Dosen".
   2. Klik tombol "Import Excel".
   3. Pilih file 'data_dosen_baru.xlsx' yang tadi dibuat.
   4. Lakukan hal yang sama untuk menu "Mahasiswa" (pilih 'data_mahasiswa_baru.xlsx').
   5. Lakukan hal yang sama untuk menu "Matakuliah".

C. MANAJEMEN DATA
   - Anda bisa Tambah (Add), Edit, atau Hapus data langsung di tabel.
   - Gunakan fitur "Cari" untuk memfilter data.

D. EXPORT DATA (Laporan)
   1. Pergi ke menu yang diinginkan (misal: Mahasiswa).
   2. Klik tombol "Export Excel".
   3. Beri nama file, lalu simpan.
   4. File Excel hasil export siap dibuka.

========================================================================
TROUBLESHOOTING
========================================================================
- Jika error "ModuleNotFoundError": Cek langkah no. 2, pastikan semua 
  pip install berhasil.
- Jika error "Connection Refused": Cek apakah PostgreSQL sudah nyala.
- Jika error "Password authentication failed": Cek file database_models.py, 
  pastikan password database benar.

========================================================================
Proudly Presented By : Zephaniah Daniel Anis & Gian Fieno Keintjem
========================================================================