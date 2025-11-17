from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date

# --- Konfigurasi Database ---
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/db_siak_tugas"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model Tabel ---

class Pengguna(Base):
    __tablename__ = "pengguna"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)

class Mahasiswa(Base):
    __tablename__ = "mahasiswa"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nim = Column(String(20), unique=True, nullable=False)
    nama = Column(String(100), nullable=False)
    program_studi = Column(String(50), nullable=False)
    gender = Column(String(1), nullable=False)
    tahun_masuk = Column(Integer, nullable=False)
    tanggal_lahir = Column(Date, nullable=True)
    status = Column(String(20), default="Aktif")

class Dosen(Base):
    __tablename__ = "dosen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nidn = Column(String(20), unique=True, nullable=False)
    nama = Column(String(100), nullable=False)
    gender = Column(String(1), nullable=False)
    jabatan_akademik = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    status = Column(String(20), default="Aktif")

class Matakuliah(Base):
    __tablename__ = "matakuliah"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kode_mk = Column(String(20), unique=True, nullable=False)
    nama_matakuliah = Column(String(100), nullable=False)
    sks = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    program_studi = Column(String(50), nullable=False)

class Nilai(Base):
    __tablename__ = "nilai"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.id", ondelete="CASCADE"), nullable=False)
    matakuliah_id = Column(Integer, ForeignKey("matakuliah.id", ondelete="CASCADE"), nullable=False)
    nilai_huruf = Column(String(2), nullable=True)      # A, B+, C, dll.
    nilai_angka = Column(Float, nullable=True)          # 4.0, 3.5, 2.0, dll.
    semester_diambil = Column(Integer, nullable=True)   # Semester saat MK diambil

    # Relasi untuk kemudahan akses
    mahasiswa = relationship("Mahasiswa", backref="nilai")
    matakuliah = relationship("Matakuliah", backref="nilai")

# --- Fungsi untuk membuat tabel ---
def create_tables():
    Base.metadata.create_all(bind=engine)
    print(f"Tabel berhasil dibuat/diperbarui di database: {DATABASE_URL.split('/')[-1]}")

if __name__ == "__main__":
    create_tables()
