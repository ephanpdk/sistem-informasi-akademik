import pandas as pd
from faker import Faker
import random
from collections import defaultdict

print("Memulai proses pembuatan data dummy...")

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

# LIST GELAR YANG DIMINTA
# Saya pasangkan dengan gelar S2 agar terlihat seperti dosen sungguhan
GELAR_MAPPING = {
    "S.Kom": "M.Kom",
    "S.E": "M.M",
    "S.Ds": "M.Ds",
    "S.T": "M.T"
}

def get_gelar_dosen():
    """Mengambil acak gelar S1 dan memasangkannya dengan S2"""
    s1 = random.choice(list(GELAR_MAPPING.keys()))
    s2 = GELAR_MAPPING[s1]
    return f"{s1}, {s2}"

# ====================================================================
# FUNGSI 1: GENERATOR MAHASISWA (Tidak Berubah)
# ====================================================================
def generate_students(num_students=200):
    print(f"Membuat {num_students} data mahasiswa...")
    data = []
    nim_counters = defaultdict(int)

    for _ in range(num_students):
        gender = random.choice(['L', 'P'])
        if gender == 'L':
            nama = f"{fake.first_name_male()} {fake.last_name_male()}"
        else:
            nama = f"{fake.first_name_female()} {fake.last_name_female()}"

        status = random.choices(["Aktif", "Cuti", "Lulus"], weights=[8, 1, 1], k=1)[0]
        tahun_masuk = random.choice([2021, 2022, 2023, 2024, 2025])
        # Logika tanggal lahir sederhana
        tahun_lahir = tahun_masuk - random.randint(18, 20)
        tanggal_lahir = fake.date_of_birth(minimum_age=18, maximum_age=22).replace(year=tahun_lahir)

        prodi_nama = random.choice(list(PRODI_KODE.keys()))
        kode_prodi = PRODI_KODE[prodi_nama]

        key = f"{tahun_masuk}_{kode_prodi}"
        nim_counters[key] += 1
        urut = f"{nim_counters[key]:03d}"
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
# FUNGSI 2: GENERATOR DOSEN (DENGAN GELAR BARU)
# ====================================================================
def generate_lecturers(num_lecturers=30):
    print(f"Membuat {num_lecturers} data dosen...")
    data = []

    for i in range(num_lecturers):
        gender = random.choice(['L', 'P'])
        
        if gender == 'L':
            prefix = fake.prefix_male()
            first = fake.first_name_male()
            last = fake.last_name_male()
        else:
            prefix = fake.prefix_female()
            first = fake.first_name_female()
            last = fake.last_name_female()

        # --- BAGIAN YANG DIUBAH ---
        # Menggunakan gelar random dari list yang diminta
        gelar_belakang = get_gelar_dosen()
        
        nama_lengkap = f"{prefix} {first} {last}, {gelar_belakang}"
        # --------------------------

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
    df.to_excel("data_dosen_baru.xlsx", index=False)
    print("-> SUKSES! File 'data_dosen_baru.xlsx' (Dengan Gelar S.Kom/S.E/dll) telah dibuat.")

# ====================================================================
# JALANKAN FUNGSI
# ====================================================================
if __name__ == "__main__":
    generate_students(100)
    generate_lecturers(30)
    print("\nSelesai!")