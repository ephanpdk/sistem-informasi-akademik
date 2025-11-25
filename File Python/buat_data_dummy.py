import pandas as pd
from faker import Faker
import random
from collections import defaultdict
import os

# Inisialisasi Faker
fake = Faker('id_ID')

# ====================================================================
# DEFINISI ATURAN & GELAR
# ====================================================================

PRODI_KODE = {
    "Sistem Informasi": "01",
    "Informatika": "02",
    "Manajemen": "03",
    "DKV": "04"
}

JABATAN_LIST = ["Asisten Ahli", "Lektor", "Lektor Kepala", "Profesor"]

GELAR_MAPPING = {
    "S.Kom": "M.Kom",
    "S.E": "M.M",
    "S.Ds": "M.Ds",
    "S.T": "M.T"
}

def get_gelar_dosen():
    s1 = random.choice(list(GELAR_MAPPING.keys()))
    s2 = GELAR_MAPPING[s1]
    return f"{s1}, {s2}"

# Daftar ID Dosen yang mungkin sudah ada di database (Asumsi ID 1 sampai 50)
dosen_ids = list(range(1, 51))

# ====================================================================
# FUNGSI 1: GENERATOR MAHASISWA
# ====================================================================

def generator_mahasiswa(num_of_students, existing_excel_file, filename="data_mahasiswa_dummy.xlsx"):
    print(f"Memulai pembuatan {num_of_students} data Mahasiswa baru...")
    
    # --- 1. Ekstraksi data dari file yang ada ---
    existing_nims = set()
    max_tahun_masuk = 2024 # Default minimal tahun masuk jika file lama tidak terbaca
    try:
        # Membaca file CSV yang diunggah
        df_existing = pd.read_csv(existing_excel_file, usecols=['NIM', 'Thn'])
        
        # Mengubah NIM lama menjadi string dan menambahkannya ke set
        existing_nims.update(df_existing['NIM'].astype(str).tolist())
        
        # Mendapatkan tahun masuk maksimum dari data lama
        max_tahun_masuk = df_existing['Thn'].max()
        
    except Exception as e:
        print(f"Peringatan: Gagal membaca file yang ada ({existing_excel_file}). Menggunakan tahun masuk maksimum default ({max_tahun_masuk}). Error: {e}")

    # --- 2. Tentukan Tahun Masuk Baru ---
    # Tahun Masuk baru harus lebih besar dari yang ada (minimal 2025)
    new_start_year = max(2025, max_tahun_masuk + 1)
    
    # Opsi tahun masuk untuk data dummy baru: new_start_year, new_start_year + 1, dst.
    tahun_masuk_pilihan = list(range(new_start_year, new_start_year + 3)) 
    print(f"-> Data dummy akan menggunakan Tahun Masuk: {min(tahun_masuk_pilihan)} - {max(tahun_masuk_pilihan)}")
    
    data = []
    generated_nims = set()
    counter = defaultdict(lambda: defaultdict(int)) 
    
    # --- 3. Generate Data Baru ---
    for i in range(1, num_of_students + 1):
        prodi = random.choice(list(PRODI_KODE.keys()))
        prodi_kode = PRODI_KODE[prodi]

        tahun_masuk = random.choice(tahun_masuk_pilihan)
        
        counter[tahun_masuk][prodi_kode] += 1
        nomor_urut = str(counter[tahun_masuk][prodi_kode]).zfill(3)
        nim = f"{tahun_masuk % 100}{prodi_kode}{nomor_urut}"
        
        # Pastikan NIM unik (di dalam file ini dan tidak ada di file lama)
        while nim in generated_nims or nim in existing_nims:
            counter[tahun_masuk][prodi_kode] += 1
            nomor_urut = str(counter[tahun_masuk][prodi_kode]).zfill(3)
            nim = f"{tahun_masuk % 100}{prodi_kode}{nomor_urut}"
            
        generated_nims.add(nim)
        
        gender = random.choice(['L', 'P'])
        
        if gender == 'L':
            first = fake.first_name_male()
            last = fake.last_name_male()
        else:
            first = fake.first_name_female()
            last = fake.last_name_female()
            
        nama_lengkap = f"{first} {last}"
        
        # Mahasiswa baru harus Aktif
        status = 'Aktif' 

        # Batasan usia yang masuk akal: 17 sampai 20 tahun
        tgl_lahir = fake.date_of_birth(minimum_age=17, maximum_age=20).strftime('%Y-%m-%d')
        
        dosen_wali = None

        data.append({
            "nim": nim,
            "nama": nama_lengkap,
            "program_studi": prodi,
            "gender": gender,
            "tahun_masuk": tahun_masuk,
            "tanggal_lahir": tgl_lahir,
            "status": status,
            "dosen_wali_id": dosen_wali
        })

    # ====================================================================
    # TAMBAHAN UNTUK MENGUJI VALIDASI
    # ====================================================================
    
    # 1. Baris dengan NIM Duplikat (menguji Mahasiswa.nim == nim check)
    if existing_nims:
        data.append({
            "nim": random.choice(list(existing_nims)), # Menggunakan NIM yang sudah ada di DB
            "nama": "DUPLIKAT NIM LAMA (Gagal)",
            "program_studi": "Informatika",
            "gender": "L",
            "tahun_masuk": 2021,
            "tanggal_lahir": fake.date_of_birth().strftime('%Y-%m-%d'),
            "status": "Aktif",
            "dosen_wali_id": None
        })

    # 2. Baris dengan Dosen Wali ID yang TIDAK ADA (menguji Foreign Key/ValueError)
    non_existent_dosen_id = max(dosen_ids) + 1 if dosen_ids else 9999
    # Menggunakan tahun masuk baru untuk NIM baru yang gagal
    nim_fail_fk = f"{tahun_masuk_pilihan[-1] % 100}99{random.randint(100, 999)}" 
    data.append({
        "nim": nim_fail_fk,
        "nama": "DOSEN TIDAK ADA (Gagal FK)",
        "program_studi": "Sistem Informasi",
        "gender": "P",
        "tahun_masuk": tahun_masuk_pilihan[-1],
        "tanggal_lahir": fake.date_of_birth().strftime('%Y-%m-%d'),
        "status": "Aktif",
        "dosen_wali_id": None
    })
    
    df = pd.DataFrame(data)
    
    # Konversi None menjadi NaN (jika belum) dan simpan ke Excel
    df['tanggal_lahir'] = df['tanggal_lahir'].replace({None: pd.NA})
    df['dosen_wali_id'] = df['dosen_wali_id'].replace({None: pd.NA})
    
    df.to_excel(filename, index=False)
    print(f"-> SUKSES! File '{filename}' telah dibuat. Terdapat {len(existing_nims)} NIM lama yang dicek.")
    return df
    
# ====================================================================
# FUNGSI 2: GENERATOR DOSEN (TIDAK BERUBAH)
# ====================================================================

def generator_dosen(num_of_lecturers, filename="data_dosen_dummy.xlsx"):
    print(f"Memulai pembuatan {num_of_lecturers} data Dosen...")
    data = []

    for i in range(1, num_of_lecturers + 1):
        gender = random.choice(['L', 'P'])
        
        if gender == 'L':
            prefix = fake.prefix_male()
            first = fake.first_name_male()
            last = fake.last_name_male()
        else:
            prefix = fake.prefix_female()
            first = fake.first_name_female()
            last = fake.last_name_female()

        gelar_belakang = get_gelar_dosen()
        
        nama_lengkap = f"{prefix} {first} {last}, {gelar_belakang}"

        jabatan = random.choice(JABATAN_LIST)
        nidn = fake.unique.random_number(digits=10)
        
        clean_name = first.lower().replace(',', '').replace('.', '') + str(i)
        
        data.append({
            "NIDN": nidn,
            "Nama": nama_lengkap,
            "Gender": gender,
            "Jabatan Akademik": jabatan,
            "Email": f"{clean_name}@kampus.ac.id"
        })

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"-> SUKSES! File '{filename}' telah dibuat.")
    return df

# ====================================================================
# JALANKAN GENERATOR 
# ====================================================================

if __name__ == "__main__":
    # Nama file excel mahasiswa lama yang digunakan sebagai referensi NIM dan Tahun Masuk maksimum.
    existing_mahasiswa_file = "mahasiswa.xlsx - Sheet1.csv" 
    
    # Ini akan membuat 100 data Mahasiswa baru (NIM lebih besar/baru)
    generator_mahasiswa(
        num_of_students=100, 
        existing_excel_file=existing_mahasiswa_file
    )
    
    # Ini membuat 25 data Dosen (tidak berubah)
    generator_dosen(num_of_lecturers=25)