from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date

# --- Konfigurasi Database ---
# Pastikan username, password, dan nama database sesuai
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/db_siak_tugas"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model Tabel ---

class Pengguna(Base):
    __tablename__ = "pengguna"
    # SQL: id integer default nextval...
    id = Column(Integer, primary_key=True, autoincrement=True)
    # SQL: username varchar(50)
    username = Column(String(50), unique=True, nullable=False)
    # SQL: hashed_password varchar(255) -> Diupdate dari 100 ke 255
    hashed_password = Column(String(255), nullable=False)
    # SQL: role varchar(50) -> Diupdate dari 20 ke 50
    role = Column(String(50), nullable=False)

class Dosen(Base):
    __tablename__ = "dosen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # SQL: nidn varchar(20)
    nidn = Column(String(20), unique=True, nullable=False)
    # SQL: nama varchar(100)
    nama = Column(String(100), nullable=False)
    # SQL: gender char(1)
    gender = Column(String(1), nullable=False)
    # SQL: jabatan_akademik varchar(50)
    jabatan_akademik = Column(String(50), nullable=True)
    # SQL: email varchar(100)
    email = Column(String(100), unique=True, nullable=False)
    # SQL: status varchar(20)
    status = Column(String(20), default="Aktif")

    # Relasi Balik: Agar bisa memanggil dosen.mahasiswa_bimbingan
    # Ini akan berisi list semua mahasiswa yang dibimbing dosen ini
    mahasiswa_bimbingan = relationship("Mahasiswa", back_populates="dosen_wali")

class Mahasiswa(Base):
    __tablename__ = "mahasiswa"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # SQL: nim varchar(50) -> Diupdate dari 20 ke 50
    nim = Column(String(50), unique=True, nullable=False)
    # SQL: nama varchar(255) -> Diupdate dari 100 ke 255
    nama = Column(String(255), nullable=False)
    # SQL: program_studi varchar(255) -> Diupdate dari 50 ke 255
    program_studi = Column(String(255), nullable=False)
    # SQL: gender varchar(1)
    gender = Column(String(1), nullable=False)
    # SQL: tahun_masuk integer
    tahun_masuk = Column(Integer, nullable=False)
    # SQL: tanggal_lahir date
    tanggal_lahir = Column(Date, nullable=True)
    # SQL: status varchar(50) -> Diupdate dari 20 ke 50
    status = Column(String(50), default="Aktif")

    # --- FITUR BARU: ACADEMIC ADVISOR (DOSEN WALI) ---
    # Menambahkan Foreign Key ke tabel Dosen
    dosen_wali_id = Column(Integer, ForeignKey("dosen.id"), nullable=True)
    
    # Relasi SQLAlchemy: Agar bisa memanggil mahasiswa.dosen_wali.nama
    dosen_wali = relationship("Dosen", back_populates="mahasiswa_bimbingan")

class Matakuliah(Base):
    __tablename__ = "matakuliah"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kode_mk = Column(String(20), unique=True, nullable=False)
    nama_matakuliah = Column(String(100), nullable=False)
    sks = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=True) # SQL nullable=True
    # SQL: program_studi varchar(100) -> Diupdate dari 50 ke 100
    program_studi = Column(String(100), nullable=False)

class Nilai(Base):
    __tablename__ = "nilai"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.id", ondelete="CASCADE"), nullable=False)
    matakuliah_id = Column(Integer, ForeignKey("matakuliah.id", ondelete="CASCADE"), nullable=False)
    nilai_huruf = Column(String(2), nullable=True)
    nilai_angka = Column(Float, nullable=True)
    semester_diambil = Column(Integer, nullable=True)

    # Relasi
    mahasiswa = relationship("Mahasiswa", backref="nilai")
    matakuliah = relationship("Matakuliah", backref="nilai")

# --- Fungsi untuk membuat tabel (Hanya berjalan jika tabel belum ada) ---
def create_tables():
    Base.metadata.create_all(bind=engine)
    print(f"Struktur tabel telah disinkronkan dengan database.")

if __name__ == "__main__":
    create_tables()