import pandas as pd
from faker import Faker
import random
from collections import defaultdict

print("Memulai proses pembuatan data dummy...")

# Inisialisasi Faker
fake = Faker('id_ID')  # Menggunakan data Indonesia

# ====================================================================
# DEFINISI ATURAN
# ====================================================================

# 1. Definisi Program Studi + Kode
PRODI_KODE = {
    "Sistem Informasi": "01",
    "Informatika": "02",
    "Manajemen": "03",
    "DKV": "04"
}

# 2. Definisi Dosen
JABATAN_LIST = ["Asisten Ahli", "Lektor", "Lektor Kepala", "Profesor"]

# ====================================================================
# FUNGSI 1: GENERATOR MAHASISWA 
# ====================================================================
def generate_students(num_students=200):  # Ganti angka untuk banyak baris
    print(f"Membuat {num_students} data mahasiswa...")
    data = []
    nim_counters = defaultdict(int)  # Counter unik per kombinasi tahun + prodi

    for _ in range(num_students):
        gender = random.choice(['L', 'P'])
        nama = fake.name_male() if gender == 'L' else fake.name_female()
        status = random.choices(["Aktif", "Cuti", "Lulus"], weights=[8, 1, 1], k=1)[0]
        
        tahun_masuk = random.choice([2021, 2022, 2023, 2024, 2025])
        tahun_lahir = tahun_masuk - random.randint(18, 20)
        tanggal_lahir = fake.date_of_birth(minimum_age=0, maximum_age=0).replace(year=tahun_lahir)

        # Pilih prodi dan ambil kodenya
        prodi_nama = random.choice(list(PRODI_KODE.keys()))
        kode_prodi = PRODI_KODE[prodi_nama]

        # Counter berdasarkan (tahun_masuk, kode_prodi)
        key = f"{tahun_masuk}_{kode_prodi}"
        nim_counters[key] += 1
        urut = f"{nim_counters[key]:03d}"  # 3 digit urut: 001, 002, ...

        # Format NIM: 2 digit tahun + 2 digit kode prodi + 3 digit urut
        nim = f"{tahun_masuk % 100:02d}{kode_prodi}{urut}"

        data.append({
            "NIM": nim,
            "Nama": nama,
            "Program Studi": prodi_nama,
            "Gender": gender,
            "Tahun Masuk": tahun_masuk,
            "Tanggal Lahir": tanggal_lahir,
            "Status": status
        })

    df = pd.DataFrame(data)
    df.to_excel("data_mahasiswa_baru.xlsx", index=False)
    print("-> SUKSES! File 'data_mahasiswa_baru.xlsx' telah dibuat.")

# ====================================================================
# FUNGSI 2: GENERATOR DOSEN 
# ====================================================================
def generate_lecturers(num_lecturers=30):
    print(f"Membuat {num_lecturers} data dosen...")
    data = []

    for i in range(num_lecturers):
        gender = random.choice(['L', 'P'])
        nama = f"{fake.prefix_male() if gender == 'L' else fake.prefix_female()} {fake.name_male() if gender == 'L' else fake.name_female()}, {fake.suffix_male() if gender == 'L' else fake.suffix_female()}"
        status = random.choices(["Aktif", "Pensiun"], weights=[9, 1], k=1)[0]
        jabatan = random.choice(JABATAN_LIST)
        nidn = fake.unique.random_number(digits=10)
        email_nama = nama.split(' ')[1].lower().replace(',', '') + str(i)
        
        data.append({
            "NIDN": nidn,
            "Nama": nama,
            "Gender": gender,
            "Jabatan Akademik": jabatan,
            "Email": f"{email_nama}@kampus.ac.id",
            "Status": status
        })

    df = pd.DataFrame(data)
    df.to_excel("data_dosen_baru.xlsx", index=False)
    print("-> SUKSES! File 'data_dosen_baru.xlsx' telah dibuat.")

# ====================================================================
# JALANKAN FUNGSI
# ====================================================================
if __name__ == "__main__":
    generate_students(100)
    generate_lecturers(30)
    print("\nFile dummy data mahasiswa dan dosen berhasil dibuat!")
    print("Silakan impor file .xlsx ini ke aplikasi Anda.")
