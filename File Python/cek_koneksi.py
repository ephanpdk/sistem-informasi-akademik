import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# --- KONFIGURASI KONEKSI DATABASE ---
# Ganti ini sesuai dengan pengaturan Anda.
# Format: "postgresql+psycopg2://<user>:<password>@<host>:<port>/<database_name>"

DB_USER = "postgres"
DB_PASSWORD = "postgres"  # <-- GANTI DENGAN PASSWORD ANDA
DB_HOST = "localhost"
DB_PORT = "5432"  # Port default PostgreSQL
DB_NAME = "db_siak_tugas"

# Buat Connection String
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --------------------------------------

def tes_koneksi():
    try:
        # Buat "mesin" yang mengelola koneksi
        engine = create_engine(DATABASE_URL)

        # Coba hubungkan
        with engine.connect() as connection:
            # Jalankan kueri sederhana untuk menguji
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()
            
            print("==============================================")
            print(f"SELAMAT! Koneksi ke database '{DB_NAME}' berhasil!")
            print(f"Versi Database: {db_version[0]}")
            print("==============================================")
            return True

    except OperationalError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"KONEKSI GAGAL. Error: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("TIPS: Periksa kembali detail di bawah ini:")
        print(f"  - Apakah nama database '{DB_NAME}' sudah benar?")
        print(f"  - Apakah password '{DB_PASSWORD}' sudah benar?")
        print(f"  - Apakah server PostgreSQL sudah berjalan?")
        return False
    except Exception as e:
        print(f"Terjadi error yang tidak terduga: {e}")
        return False

if __name__ == "__main__":
    tes_koneksi()