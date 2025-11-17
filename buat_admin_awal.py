import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Import 'SessionLocal' dan 'Pengguna' dari file yang kita buat sebelumnya
from database_models import SessionLocal, Pengguna 

# --- DATA ADMIN YANG INGIN DIBUAT ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123" # Password sederhana untuk tugas
ADMIN_ROLE = "Admin Manajemen"
# -----------------------------------

def buat_admin_pertama():
    print(f"Mencoba membuat super admin (Username: {ADMIN_USERNAME})...")
    
    # Buka koneksi (jendela) ke database
    db_session = SessionLocal() 
    
    try:
        # 1. Cek dulu apakah 'admin' sudah ada
        # Ini agar skripnya aman dijalankan berkali-kali
        admin_ada = db_session.query(Pengguna).filter_by(username=ADMIN_USERNAME).first()
        
        if admin_ada:
            print(f"-> PENGGUNA '{ADMIN_USERNAME}' SUDAH ADA. Tidak ada yang dilakukan.")
            return

        # 2. Jika tidak ada, kita hash passwordnya
        # (ubah password string menjadi byte, lalu hash)
        password_bytes = ADMIN_PASSWORD.encode('utf-8')
        # 'bcrypt' adalah algoritma hashing yang kuat
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        
        # 3. Buat objek Pengguna baru
        # (Pastikan hash-nya di-decode kembali jadi string agar bisa disimpan di DB)
        admin_baru = Pengguna(
            username=ADMIN_USERNAME,
            hashed_password=hashed_password.decode('utf-8'), # Simpan sebagai string
            role=ADMIN_ROLE
        )
        
        # 4. Masukkan ke database
        db_session.add(admin_baru)  # Tambahkan ke "sesi"
        db_session.commit()         # Simpan perubahan secara permanen
        
        print(f"-> SUKSES! Pengguna '{ADMIN_USERNAME}' (Role: {ADMIN_ROLE}) telah dibuat.")
        print(f"-> Passwordnya adalah: {ADMIN_PASSWORD} (Harap diingat!)")
        
    except Exception as e:
        db_session.rollback() # Batalkan jika ada error
        print(f"Terjadi error saat membuat admin: {e}")
    finally:
        db_session.close() # Selalu tutup koneksi (jendela)
        
# --------------------------------------------------
# Jalankan fungsi ini jika file ini dieksekusi
if __name__ == "__main__":
    buat_admin_pertama()