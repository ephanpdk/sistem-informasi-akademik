import pandas as pd
from faker import Faker
import random
from collections import defaultdict

fake = Faker('id_ID')

PRODI_KODE = {
    "Sistem Informasi": "01",
    "Informatika": "02",
    "Manajemen": "03",
    "DKV": "04"
}

def generator_mahasiswa_baru(jumlah_data, nama_file_output="data_mahasiswa_dummy_baru.xlsx"):
    data = []
    counter = defaultdict(lambda: defaultdict(int))
    
    tahun_pilihan = [2024, 2025]
    
    for _ in range(jumlah_data):
        prodi_nama = random.choice(list(PRODI_KODE.keys()))
        prodi_kode = PRODI_KODE[prodi_nama]
        
        thn = random.choice(tahun_pilihan)
        
        counter[thn][prodi_kode] += 1
        urutan = counter[thn][prodi_kode]
        
        yy = str(thn)[-2:]
        nim = f"{yy}{prodi_kode}{urutan:03d}"
        
        gender = random.choice(['L', 'P'])
        if gender == 'L':
            nama = f"{fake.first_name_male()} {fake.last_name_male()}"
        else:
            nama = f"{fake.first_name_female()} {fake.last_name_female()}"
            
        tgl_lahir = fake.date_of_birth(minimum_age=17, maximum_age=22)
        tgl = tgl_lahir.strftime("%d/%m/%Y")
        
        row = {
            "NIM": nim,
            "Nama": nama,
            "Prodi": prodi_nama,
            "LP": gender,
            "Thn": thn,
            "Tgl": tgl,
            "Status": "Aktif",
            "Doswal": None
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df = df[['NIM', 'Nama', 'Prodi', 'LP', 'Thn', 'Tgl', 'Status', 'Doswal']]
    
    df.to_excel(nama_file_output, index=False)
    print(f"File {nama_file_output} berhasil dibuat dengan {jumlah_data} data.")

if __name__ == "__main__":
    generator_mahasiswa_baru(100)