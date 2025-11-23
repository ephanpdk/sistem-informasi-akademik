import pandas as pd

# 1. Data Dummy Informatika (Format: INF[Semester][Urutan])
data_informatika = [
    # Semester 1
    ['INF101', 'Kalkulus Dasar', 3, 1, 'Informatika'],
    ['INF102', 'Fisika Dasar', 3, 1, 'Informatika'],
    ['INF103', 'Logika Matematika', 3, 1, 'Informatika'],
    ['INF104', 'Bahasa Inggris Teknis', 2, 1, 'Informatika'],
    ['INF105', 'Pengantar Teknologi Informasi', 2, 1, 'Informatika'],
    ['INF106', 'Algoritma & Pemrograman Dasar', 4, 1, 'Informatika'],
    # Semester 2
    ['INF201', 'Matematika Diskrit', 3, 2, 'Informatika'],
    ['INF202', 'Aljabar Linear', 3, 2, 'Informatika'],
    ['INF203', 'Struktur Data', 4, 2, 'Informatika'],
    ['INF204', 'Arsitektur & Organisasi Komputer', 3, 2, 'Informatika'],
    ['INF205', 'Interaksi Manusia dan Komputer', 3, 2, 'Informatika'],
    ['INF206', 'Pendidikan Kewarganegaraan', 2, 2, 'Informatika'],
    # Semester 3
    ['INF301', 'Sistem Operasi', 3, 3, 'Informatika'],
    ['INF302', 'Pemrograman Berorientasi Objek', 4, 3, 'Informatika'],
    ['INF303', 'Basis Data I', 4, 3, 'Informatika'],
    ['INF304', 'Jaringan Komputer Dasar', 3, 3, 'Informatika'],
    ['INF305', 'Probabilitas dan Statistik', 3, 3, 'Informatika'],
    ['INF306', 'Analisis Algoritma', 3, 3, 'Informatika'],
    # Semester 4
    ['INF401', 'Rekayasa Perangkat Lunak', 3, 4, 'Informatika'],
    ['INF402', 'Basis Data Lanjut', 3, 4, 'Informatika'],
    ['INF403', 'Pemrograman Web', 4, 4, 'Informatika'],
    ['INF404', 'Teori Bahasa & Otomata', 3, 4, 'Informatika'],
    ['INF405', 'Keamanan Jaringan', 3, 4, 'Informatika'],
    # Semester 5
    ['INF501', 'Kecerdasan Buatan (AI)', 3, 5, 'Informatika'],
    ['INF502', 'Pemrograman Mobile', 4, 5, 'Informatika'],
    ['INF503', 'Pengolahan Citra Digital', 3, 5, 'Informatika'],
    ['INF504', 'Sistem Terdistribusi', 3, 5, 'Informatika'],
    ['INF505', 'Metode Numerik', 2, 5, 'Informatika'],
    # Semester 6
    ['INF601', 'Pembelajaran Mesin (Machine Learning)', 3, 6, 'Informatika'],
    ['INF602', 'Cloud Computing', 3, 6, 'Informatika'],
    ['INF603', 'Manajemen Proyek TI', 3, 6, 'Informatika'],
    ['INF604', 'Kerja Praktik / Magang', 4, 6, 'Informatika'],
    ['INF605', 'Etika Profesi', 2, 6, 'Informatika'],
    # Semester 7
    ['INF701', 'Metodologi Penelitian', 2, 7, 'Informatika'],
    ['INF702', 'Kewirausahaan Berbasis Teknologi', 2, 7, 'Informatika'],
    ['INF703', 'Data Mining', 3, 7, 'Informatika'],
    ['INF704', 'Tugas Akhir 1 (Pra-Skripsi)', 2, 7, 'Informatika']
]

# 2. Data Prodi Lain
data_prodi_lain = [
    # Sistem Informasi
    ['SI101','Pengantar Sistem Informasi',3,1,'Sistem Informasi'],
    ['SI102','Logika dan Algoritma',3,1,'Sistem Informasi'],
    ['SI103','Dasar-Dasar Pemrograman',3,1,'Sistem Informasi'],
    ['SI104','Pengantar Bisnis dan Manajemen',3,1,'Sistem Informasi'],
    ['SI201','Analisis Proses Bisnis',3,2,'Sistem Informasi'],
    ['SI202','Basis Data',4,2,'Sistem Informasi'],
    ['SI203','Matematika Bisnis',3,2,'Sistem Informasi'],
    ['SI204','Akuntansi Dasar',3,2,'Sistem Informasi'],
    ['SI301','Analisis dan Perancangan Sistem',4,3,'Sistem Informasi'],
    ['SI302','Jaringan Komputer',3,3,'Sistem Informasi'],
    ['SI303','Interaksi Manusia dan Komputer',3,3,'Sistem Informasi'],
    ['SI401','Manajemen Proyek SI',3,4,'Sistem Informasi'],
    ['SI402','E-Business dan E-Commerce',3,4,'Sistem Informasi'],
    ['SI403','Sistem Enterprise (ERP)',3,4,'Sistem Informasi'],
    ['SI501','Keamanan Sistem Informasi',3,5,'Sistem Informasi'],
    ['SI502','Business Intelligence & Data Warehouse',3,5,'Sistem Informasi'],
    ['SI601','Audit Sistem Informasi',3,6,'Sistem Informasi'],
    ['SI602','Tata Kelola TI',3,6,'Sistem Informasi'],
    ['SI701','Kerja Praktek',2,7,'Sistem Informasi'],
    ['SI702','Skripsi',6,7,'Sistem Informasi'],
    
    # DKV
    ['DKV101','Nirmana Dwimatra',3,1,'DKV'],
    ['DKV102','Gambar Bentuk',3,1,'DKV'],
    ['DKV103','Sejarah Seni Rupa dan Desain',2,1,'DKV'],
    ['DKV104','Pengantar DKV',2,1,'DKV'],
    ['DKV201','Tipografi Dasar',3,2,'DKV'],
    ['DKV202','Ilustrasi Dasar',3,2,'DKV'],
    ['DKV203','Fotografi Dasar',3,2,'DKV'],
    ['DKV204','Software Desain Grafis',2,2,'DKV'],
    ['DKV301','Desain Grafis Periklanan',4,3,'DKV'],
    ['DKV302','Desain Identitas Visual',3,3,'DKV'],
    ['DKV303','Videografi',3,3,'DKV'],
    ['DKV401','Desain Web dan Antarmuka (UI/UX)',3,4,'DKV'],
    ['DKV402','Animasi 2D',3,4,'DKV'],
    ['DKV403','Desain Publikasi',3,4,'DKV'],
    ['DKV501','Manajemen Desain',2,5,'DKV'],
    ['DKV502','Komunikasi Pemasaran Visual',3,5,'DKV'],
    ['DKV601','Portofolio Desain',3,6,'DKV'],
    ['DKV602','Desain Kemasan',3,6,'DKV'],
    ['DKV701','Magang Industri',3,7,'DKV'],
    ['DKV702','Tugas Akhir Karya',6,7,'DKV'],

    # Manajemen
    ['MNJ101','Pengantar Manajemen',3,1,'Manajemen'],
    ['MNJ102','Pengantar Bisnis',3,1,'Manajemen'],
    ['MNJ103','Matematika Ekonomi',3,1,'Manajemen'],
    ['MNJ104','Pengantar Akuntansi',3,1,'Manajemen'],
    ['MNJ201','Manajemen Pemasaran',3,2,'Manajemen'],
    ['MNJ202','Manajemen Keuangan',3,2,'Manajemen'],
    ['MNJ203','Manajemen SDM',3,2,'Manajemen'],
    ['MNJ204','Statistika Bisnis',3,2,'Manajemen'],
    ['MNJ301','Manajemen Operasional',3,3,'Manajemen'],
    ['MNJ302','Perilaku Organisasi',3,3,'Manajemen'],
    ['MNJ303','Ekonomi Manajerial',3,3,'Manajemen'],
    ['MNJ401','Manajemen Strategis',3,4,'Manajemen'],
    ['MNJ402','Akuntansi Biaya',3,4,'Manajemen'],
    ['MNJ403','Riset Pemasaran',3,4,'Manajemen'],
    ['MNJ501','Studi Kelayakan Bisnis',3,5,'Manajemen'],
    ['MNJ502','Kewirausahaan',3,5,'Manajemen'],
    ['MNJ601','Manajemen Investasi',3,6,'Manajemen'],
    ['MNJ602','Manajemen Pemasaran Global',3,6,'Manajemen'],
    ['MNJ701','Kuliah Kerja Nyata (KKN)',3,7,'Manajemen'],
    ['MNJ702','Skripsi',6,7,'Manajemen']
]

# 3. Gabungkan Data
all_data = data_informatika + data_prodi_lain

# 4. PENTING: Nama Kolom Disesuaikan dengan `main.py`
columns = ['Kode MK', 'Nama Matakuliah', 'SKS', 'Semester', 'Program Studi']

# 5. Buat DataFrame
df = pd.DataFrame(all_data, columns=columns)

# 6. Export ke Excel
file_name = 'data_matakuliah_fix_import.xlsx'
df.to_excel(file_name, index=False)

print(f"File berhasil dibuat: {file_name}")
print("Kolom yang digunakan:", columns)
print(f"Total Baris Data: {len(df)}")