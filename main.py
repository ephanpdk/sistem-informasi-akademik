import sys
import bcrypt
import pandas as pd 
from collections import defaultdict
from datetime import datetime
from sqlalchemy import func
from PySide6.QtCore import Qt, Signal, QDate, QSortFilterProxyModel, QMargins, QRect, QSize
from PySide6.QtGui import QIntValidator, QStandardItemModel, QStandardItem, QPainter, QFont, QColor, QPageSize, QPixmap
from PySide6.QtWidgets import (
    QApplication, 
    QWidget, 
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QVBoxLayout,
    QHBoxLayout, 
    QFrame,     
    QMessageBox,
    QMainWindow, 
    QStackedWidget,
    QSpacerItem,     
    QSizePolicy,
    QTableWidget,    
    QTableWidgetItem, 
    QHeaderView,      
    QFormLayout,      
    QDateEdit,        
    QComboBox,
    QFileDialog,
    QCompleter 
)
# --- IMPORT BARU UNTUK GRAFIK ---
try:
    from PySide6.QtCharts import (
        QChart, QChartView, QLineSeries, QValueAxis, 
        QScatterSeries, QBarSeries, QBarSet, QBarCategoryAxis,
        QPieSeries, QPieSlice, QStackedBarSeries # Pastikan semua ini ada
    )
except ImportError:
    print("="*50)
    print("ERROR: Modul PySide6.QtCharts tidak ditemukan.")
    print("Silakan instal dengan: pip install PySide6-Addons")
    print("="*50)
    sys.exit(1)

try:
    from database_models import SessionLocal, Pengguna, Mahasiswa, Dosen, Matakuliah, Nilai
except ImportError:
    print("PERINGATAN: Gagal mengimpor 'database_models'.")
    print("Pastikan file 'database_models.py' dan 'create_db.py' ada dan sudah dijalankan.")
    pass

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

try:
    from PySide6.QtPrintSupport import QPrinter
except ImportError:
    print("Modul QtPrintSupport tidak ditemukan. Pastikan instalasi PySide6 lengkap.")

# ====================================================================
# --- KARTU 1: Halaman Login ---
# ====================================================================
class LoginWidget(QWidget):
    login_success_signal = Signal(str, str) 

    def __init__(self):
        super().__init__()
        self.initUI()
        self.applyStyles()

    def initUI(self):
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(30, 30, 30, 30) 
        form_layout.setSpacing(15) 
        self.title_label = QLabel("LOGIN")
        self.title_label.setObjectName("title_label") 
        self.title_label.setAlignment(Qt.AlignCenter)
        self.label_username = QLabel("Username") 
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username Anda")
        self.label_password = QLabel("Password") 
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Masukkan password Anda")
        self.input_password.setEchoMode(QLineEdit.Password) 
        self.button_login = QPushButton("Login")
        self.button_login.setObjectName("login_button") 
        self.button_login.clicked.connect(self.handle_login)
        form_layout.addWidget(self.title_label)
        form_layout.addSpacing(20) 
        form_layout.addWidget(self.label_username)
        form_layout.addWidget(self.input_username)
        form_layout.addSpacing(5) 
        form_layout.addWidget(self.label_password)
        form_layout.addWidget(self.input_password)
        form_layout.addSpacing(25) 
        form_layout.addWidget(self.button_login)
        form_layout.addStretch() 
        self.login_frame = QFrame()
        self.login_frame.setObjectName("login_frame") 
        self.login_frame.setLayout(form_layout) 
        self.login_frame.setFixedSize(400, 450)
        h_layout = QHBoxLayout()
        h_layout.addStretch() 
        h_layout.addWidget(self.login_frame) 
        h_layout.addStretch() 
        main_layout = QVBoxLayout()
        main_layout.addStretch() 
        main_layout.addLayout(h_layout) 
        main_layout.addStretch() 
        self.setLayout(main_layout)

    def applyStyles(self):
        self.setStyleSheet("""
            LoginWidget { background-color: #FFFFFF; }
            #login_frame {
                background-color: #F0F2F5; 
                border-radius: 10px;
                border: 1px solid #E5E7EB;
            }
            #title_label {
                font-size: 28px;
                font-weight: bold;
                color: #000000;
            }
            QLabel {
                font-size: 14px;
                color: #000000;
                font-weight: 600; 
            }
            QLineEdit {
                font-size: 14px;
                background-color: #FFFFFF; 
                border: 1px solid #E0E0E0; 
                border-radius: 5px;
                padding: 10px; 
                color: #000000; 
            }
            QLineEdit:focus { border: 1px solid #0078D7; }
            #login_button {
                font-size: 15px; font-weight: bold;
                background-color: #0078D7; color: white;
                border: none; border-radius: 5px; padding: 12px;
            }
            #login_button:hover { background-color: #005A9E; }
            #login_button:pressed { background-color: #004A8C; }
        """)

    def handle_login(self):
        username_input = self.input_username.text()
        password_input = self.input_password.text()
        if not username_input or not password_input:
            self.show_message("Error", "Username dan password tidak boleh kosong.")
            return
        
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            pengguna = db_session.query(Pengguna).filter_by(username=username_input).first()
            if pengguna:
                password_bytes = password_input.encode('utf-8')
                hashed_password_bytes = pengguna.hashed_password.encode('utf-8')
                if bcrypt.checkpw(password_bytes, hashed_password_bytes):
                    self.login_success_signal.emit(pengguna.username, pengguna.role)
                else:
                    self.show_message("Error", "Password salah.")
            else:
                self.show_message("Error", "Username tidak ditemukan.")
        except Exception as e:
            self.show_message("Error", f"Terjadi error koneksi: {e}")
        finally:
            db_session.close()

    def show_message(self, title, message):
        msg_box = QMessageBox()
        if title == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_text = f"<p style='font-size: 14px;'>{message}</p>"
        msg_box.setText(msg_text)
        msg_box.exec()

# ====================================================================
# --- KELAS: Halaman CRUD Mahasiswa ---
# ====================================================================
class MahasiswaWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.selected_mahasiswa_id = None
        
        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.form_frame = QFrame() 
        self.form_frame.setObjectName("form_frame") 
        self.form_frame.setEnabled(False) 
        form_layout = QFormLayout() 
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        self.input_nim = QLineEdit()
        self.input_nama = QLineEdit()
        self.input_prodi = QLineEdit() 
        self.input_gender = QComboBox()
        self.input_gender.addItems(["L", "P"]) 
        self.input_tahun_masuk = QLineEdit()
        self.input_tahun_masuk.setValidator(QIntValidator(1980, 2099)) 
        self.input_tahun_masuk.setMaxLength(4)
        self.input_tgl_lahir = QDateEdit()
        self.input_tgl_lahir.setCalendarPopup(True)
        self.input_tgl_lahir.setDate(QDate.currentDate())
        self.input_tgl_lahir.setDisplayFormat("dd/MM/yyyy")
        self.input_status = QComboBox()
        self.input_status.addItems(["Aktif", "Cuti", "Lulus", "DO"])
        self.input_dosen_wali = QComboBox()
        self.input_dosen_wali.setEditable(True)
        self.input_dosen_wali.setInsertPolicy(QComboBox.NoInsert)
        self.input_dosen_wali.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.input_dosen_wali.completer().setFilterMode(Qt.MatchContains) 
        completer_popup = self.input_dosen_wali.completer().popup()
        completer_popup.setStyleSheet("""
            QListView {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #E0E0E0;
                font-size: 14px;
            }
            QListView::item:selected {
                background-color: #0078D7;
                color: #FFFFFF;
            }
        """)
        
        self.input_dosen_wali.addItem("-- Pilih Dosen Wali --", None)
        form_layout.addRow(QLabel("NIM:"), self.input_nim)
        form_layout.addRow(QLabel("Nama Lengkap:"), self.input_nama)
        form_layout.addRow(QLabel("Program Studi:"), self.input_prodi) 
        form_layout.addRow(QLabel("Gender (L/P):"), self.input_gender)
        form_layout.addRow(QLabel("Tahun Masuk:"), self.input_tahun_masuk)
        form_layout.addRow(QLabel("Tanggal Lahir:"), self.input_tgl_lahir)
        form_layout.addRow(QLabel("Status:"), self.input_status)
        form_layout.addRow(QLabel("Dosen Wali:"), self.input_dosen_wali)
        
        btn_layout = QHBoxLayout()
        self.btn_update = QPushButton("Update Data") 
        self.btn_update.setObjectName("btn_simpan") 
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_hapus")
        self.btn_bersihkan = QPushButton("Bersihkan Form")
        self.btn_bersihkan.setObjectName("btn_bersihkan")
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_hapus)
        
        form_container_layout = QVBoxLayout(self.form_frame)
        form_container_layout.addLayout(form_layout)
        form_container_layout.addLayout(btn_layout)
        form_container_layout.addWidget(self.btn_bersihkan)
        main_layout.addWidget(self.form_frame) 

        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        button_bar_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import from Excel")
        self.btn_import.setObjectName("btn_simpan") 
        self.btn_import.setStyleSheet("font-weight: bold; padding: 10px;")
        self.btn_export = QPushButton("Export to Excel") 
        self.btn_export.setObjectName("btn_export") 
        self.btn_export.setStyleSheet("font-weight: bold; padding: 10px;")
        button_bar_layout.addWidget(self.btn_import)
        button_bar_layout.addWidget(self.btn_export) 
        button_bar_layout.addStretch() 
        table_layout.addLayout(button_bar_layout) 
        
        self.search_input = QLineEdit() 
        self.search_input.setPlaceholderText("Cari berdasarkan NIM atau Nama...")
        table_layout.addWidget(self.search_input) 
        
        self.table_mhs = QTableWidget()
        header = self.table_mhs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Kolom No: Sesuai isi
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # NIM: Sesuai isi
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Nama: MELAR (Prioritas)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Prodi: Sesuai isi (atau Stretch kalau nama prodi panjang)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Gender: Sesuai isi (kecil)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Tahun: Sesuai isi
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # Tgl Lahir
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(9, QHeaderView.Stretch)          # Dosen Wali: MELAR (Prioritas)
        self.table_mhs.setColumnCount(10) 
        self.table_mhs.setHorizontalHeaderLabels([
            "#"
            , "ID", "NIM", "Nama", "Program Studi", 
            "Gender", "Tahun Masuk", "Tgl Lahir", "Status", "Dosen Wali"
        ])
        self.table_mhs.verticalHeader().hide()
        self.table_mhs.setColumnHidden(1, True) 
        self.table_mhs.setColumnWidth(0, 50) 
        self.table_mhs.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) 
        self.table_mhs.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch) 
        self.table_mhs.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_mhs.setEditTriggers(QTableWidget.NoEditTriggers) 
        table_layout.addWidget(self.table_mhs)
        main_layout.addWidget(table_frame) 
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 3) 

        self.btn_update.clicked.connect(self.update_data) 
        self.btn_import.clicked.connect(self.import_from_excel) 
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_bersihkan.clicked.connect(self.clear_form)
        self.btn_hapus.clicked.connect(self.delete_data)
        self.table_mhs.itemClicked.connect(self.table_row_clicked)
        self.search_input.textChanged.connect(self.filter_table)
        self.load_dosen_options()
        self.applyStyles()

    def applyStyles(self):
        self.setStyleSheet("""
            MahasiswaWidget { background-color: #FFFFFF; }
            #form_frame {
                background-color: #F0F2F5;
                border-radius: 10px;
            }
            #form_frame QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QLineEdit, QDateEdit, QComboBox {
                font-size: 14px;
                background-color: #FFFFFF; 
                border: 1px solid #E0E0E0; 
                border-radius: 5px;
                padding: 8px;
                color: #000000; 
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            #form_frame QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            #btn_simpan { background-color: #0078D7; }
            #btn_simpan:hover { background-color: #005A9E; }
            #btn_simpan:pressed { background-color: #004A8C; }
            #btn_export {
                background-color: #6C757D;
            }
            #btn_export:hover { background-color: #5A6268; }
            #btn_export:pressed { background-color: #4E555B; }
            #btn_hapus { background-color: #D9534F; }
            #btn_hapus:hover { background-color: #C9302C; }
            #btn_hapus:pressed { background-color: #AC2925; }
            #btn_bersihkan { background-color: #6C757D; }
            #btn_bersihkan:hover { background-color: #5A6268; }
            #btn_bersihkan:pressed { background-color: #4E555B; }
            QTableWidget {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F7F7F7; 
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QFrame {
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                selection-background-color: #0078D7; 
                selection-color: #FFFFFF; 
                outline: 0px; 
            }
            QListView {
                color: #000000;
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
            }
            QListView::item:selected {
                background-color: #0078D7;
                color: #FFFFFF;
            }
            QCalendarWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
            }
            QCalendarWidget QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
            }
            QCalendarWidget QTableView QHeaderView::section {
                background-color: #F7F7F7;
                color: #000000; 
                font-weight: 600;
            }
            QCalendarWidget QToolButton {
                color: #000000; 
                background-color: #F7F7F7;
                border: none;
            }
            QCalendarWidget QMenu {
                background-color: #FFFFFF;
                color: #000000; 
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #0078D7;
            }
        """)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table_mhs.rowCount()):
            nim_item = self.table_mhs.item(row, 2)  
            nama_item = self.table_mhs.item(row, 3) 
            if nim_item and nama_item:
                nim_text = nim_item.text().lower()
                nama_text = nama_item.text().lower()
                if search_text in nim_text or search_text in nama_text:
                    self.table_mhs.setRowHidden(row, False)
                else:
                    self.table_mhs.setRowHidden(row, True)
    def load_dosen_options(self):
        self.input_dosen_wali.clear()
        self.input_dosen_wali.addItem("-- Pilih Dosen Wali --", None)
        
        if 'SessionLocal' not in globals(): return
        
        db = SessionLocal()
        try:
            # Ambil dosen yang statusnya aktif
            dosen_list = db.query(Dosen).filter(Dosen.status == 'Aktif').all()
            for d in dosen_list:
                # Simpan ID dosen sebagai userData (parameter kedua)
                self.input_dosen_wali.addItem(f"{d.nama}", d.id)
        except Exception as e:
            print(f"Error loading dosen: {e}")
        finally:
            db.close()
    
    def load_data(self):
        print("Memuat data mahasiswa...")
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            semua_mahasiswa = db_session.query(Mahasiswa).all()
            self.table_mhs.setRowCount(0) 
            for row_position, mhs in enumerate(semua_mahasiswa):
                self.table_mhs.insertRow(row_position)
                tgl_lahir_str = mhs.tanggal_lahir.strftime("%d/%m/%Y") if mhs.tanggal_lahir else ""
                nomor_item = QTableWidgetItem(str(row_position + 1))
                nomor_item.setTextAlignment(Qt.AlignCenter)
                self.table_mhs.setItem(row_position, 0, nomor_item) # '#'
                self.table_mhs.setItem(row_position, 1, QTableWidgetItem(str(mhs.id))) # ID
                self.table_mhs.setItem(row_position, 2, QTableWidgetItem(mhs.nim)) # NIM
                self.table_mhs.setItem(row_position, 3, QTableWidgetItem(mhs.nama)) # Nama
                self.table_mhs.setItem(row_position, 4, QTableWidgetItem(mhs.program_studi)) # Prodi (indeks 4)
                self.table_mhs.setItem(row_position, 5, QTableWidgetItem(mhs.gender)) # Gender (indeks 5)
                self.table_mhs.setItem(row_position, 6, QTableWidgetItem(str(mhs.tahun_masuk))) # Tahun Masuk (indeks 6)
                self.table_mhs.setItem(row_position, 7, QTableWidgetItem(tgl_lahir_str)) # Tgl Lahir (indeks 7)
                self.table_mhs.setItem(row_position, 8, QTableWidgetItem(mhs.status)) # Status (indeks 8)
                nama_doswal = mhs.dosen_wali.nama if mhs.dosen_wali else "-"
                self.table_mhs.setItem(row_position, 9, QTableWidgetItem(nama_doswal))
        except Exception as e:
            self.show_message("Error", f"Gagal memuat data: {e}")
        finally:
            db_session.close()

    def update_data(self):
        if not self.selected_mahasiswa_id:
            self.show_message("Error", "Pilih data dari tabel yang ingin Anda update.")
            return
        nim = self.input_nim.text()
        nama = self.input_nama.text()
        prodi = self.input_prodi.text() 
        gender = self.input_gender.currentText() 
        try:
            tahun_masuk = int(self.input_tahun_masuk.text())
        except ValueError:
            self.show_message("Error", "Tahun Masuk harus berupa angka (misal: 2023).")
            return
        tanggal_lahir = self.input_tgl_lahir.date().toPython() 
        status = self.input_status.currentText()
        dosen_wali_id = self.input_dosen_wali.currentData()
        
        if not nim or not nama or not prodi:
            self.show_message("Error", "NIM, Nama, dan Program Studi tidak boleh kosong.")
            return
            
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            mhs = db_session.query(Mahasiswa).get(self.selected_mahasiswa_id)
            if mhs:
                if mhs.nim != nim:
                    nim_ada = db_session.query(Mahasiswa).filter_by(nim=nim).first()
                    if nim_ada:
                        self.show_message("Error", f"NIM {nim} sudah terdaftar untuk mahasiswa lain.")
                        db_session.rollback()
                        return
                mhs.nim = nim
                mhs.nama = nama
                mhs.program_studi = prodi
                mhs.gender = gender
                mhs.tahun_masuk = tahun_masuk
                mhs.tanggal_lahir = tanggal_lahir
                mhs.status = status
                mhs.dosen_wali_id = dosen_wali_id
                self.show_message("Sukses", f"Data {nama} berhasil diperbarui.")
                db_session.commit()
            else:
                self.show_message("Error", "Data tidak ditemukan (mungkin sudah dihapus).")
        except Exception as e:
            db_session.rollback()
            self.show_message("Error", f"Gagal menyimpan data: {e}")
        finally:
            db_session.close()
        self.load_data()
        self.clear_form()

    def import_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        try:
            df = pd.read_excel(file_path)
            df = df.astype({
                "NIM": str, "Nama": str, 
                "Program Studi": str, "Gender": str, "Status": str, 
                "Tahun Masuk": str 
            }) 
        except Exception as e:
            self.show_message("Error", f"Gagal membaca file Excel: {e}")
            return
            
        required_columns = [
            "NIM", "Nama", "Program Studi", 
            "Gender", "Tahun Masuk", "Tanggal Lahir", "Status"
        ]
        if not all(col in df.columns for col in required_columns):
            self.show_message("Error", 
                "Format Excel salah.\nPastikan Anda memiliki kolom:\n" +
                ", ".join(required_columns)
            )
            return
            
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        added_count = 0
        skipped_count = 0
        try:
            for index, row in df.iterrows():
                nim = row["NIM"]
                prodi_excel = row["Program Studi"]
                nim_ada = db_session.query(Mahasiswa).filter_by(nim=nim).first()
                if nim_ada:
                    skipped_count += 1
                    continue
                
                gender = str(row["Gender"]).upper()
                if gender not in ['L', 'P']:
                    skipped_count += 1
                    continue
                try:
                    tahun_masuk = int(row["Tahun Masuk"])
                except:
                    skipped_count += 1
                    continue
                try:
                    tgl_lahir = pd.to_datetime(row["Tanggal Lahir"]).date()
                except:
                    tgl_lahir = None 
                mhs_baru = Mahasiswa(
                    nim=nim, nama=row["Nama"], 
                    program_studi=prodi_excel, gender=gender,
                    tahun_masuk=tahun_masuk, tanggal_lahir=tgl_lahir,
                    status=row["Status"]
                )
                db_session.add(mhs_baru)
                added_count += 1
            db_session.commit()
            self.show_message("Sukses", 
                f"Import Selesai.\n\n"
                f"Data baru ditambahkan: {added_count}\n"
                f"Data duplikat/salah format dilewati: {skipped_count}"
            )
        except Exception as e:
            db_session.rollback()
            self.show_message("Error", f"Terjadi error saat import: {e}")
        finally:
            db_session.close()
        self.load_data()

    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan File Excel",
            "export_mahasiswa.xlsx", 
            "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        data_to_export = []
        headers = []
        for col in range(self.table_mhs.columnCount()):
            if not self.table_mhs.isColumnHidden(col):
                headers.append(self.table_mhs.horizontalHeaderItem(col).text())
        for row in range(self.table_mhs.rowCount()):
            if not self.table_mhs.isRowHidden(row):
                row_data = []
                for col in range(self.table_mhs.columnCount()):
                    if not self.table_mhs.isColumnHidden(col):
                        item = self.table_mhs.item(row, col)
                        row_data.append(item.text() if item else "")
                data_to_export.append(row_data)
        try:
            df = pd.DataFrame(data_to_export, columns=headers)
            df.to_excel(file_path, index=False)
            self.show_message("Sukses", f"Data berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            self.show_message("Error", f"Gagal mengekspor file: {e}")

    def delete_data(self):
        if not self.selected_mahasiswa_id:
            self.show_message("Error", "Pilih data dari tabel yang ingin dihapus.")
            return
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"<p style='font-size: 14px;'>Apakah Anda yakin ingin menghapus data dengan ID {self.selected_mahasiswa_id}?</p>")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        if msg_box.exec() == QMessageBox.Yes:
            if 'SessionLocal' not in globals():
                self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
                return
                
            db_session = SessionLocal()
            try:
                mhs = db_session.query(Mahasiswa).get(self.selected_mahasiswa_id)
                if mhs:
                    db_session.delete(mhs)
                    db_session.commit()
                    self.show_message("Sukses", "Data berhasil dihapus.")
                else:
                    self.show_message("Error", "Data tidak ditemukan.")
            except Exception as e:
                db_session.rollback()
                self.show_message("Error", f"Gagal menghapus data: {e}")
            finally:
                db_session.close()
            self.load_data()
            self.clear_form()

    def clear_form(self):
        self.selected_mahasiswa_id = None 
        self.input_nim.clear()
        self.input_nama.clear()
        self.input_prodi.clear() 
        self.input_gender.setCurrentIndex(0) 
        self.input_tahun_masuk.clear()
        self.input_tgl_lahir.setDate(QDate.currentDate())
        self.input_status.setCurrentIndex(0)
        self.form_frame.setEnabled(False) 
        self.input_nim.setReadOnly(False) 

    def table_row_clicked(self, item):
        self.form_frame.setEnabled(True) 
        self.input_nim.setReadOnly(False) 
        row = item.row()
        
        mhs_id = int(self.table_mhs.item(row, 1).text())
        nim = self.table_mhs.item(row, 2).text()
        nama = self.table_mhs.item(row, 3).text()
        prodi = self.table_mhs.item(row, 4).text() 
        gender = self.table_mhs.item(row, 5).text() 
        tahun_masuk = self.table_mhs.item(row, 6).text() 
        tgl_lahir_str = self.table_mhs.item(row, 7).text() 
        status = self.table_mhs.item(row, 8).text() 
        dosen_wali_nama = self.table_mhs.item(row, 9).text()
        
        try:
            tanggal_lahir = QDate.fromString(tgl_lahir_str, "dd/MM/yyyy")
        except:
            tanggal_lahir = QDate.currentDate()
            
        self.selected_mahasiswa_id = mhs_id
        self.input_nim.setText(nim)
        self.input_nama.setText(nama)
        self.input_prodi.setText(prodi) 
        self.input_gender.setCurrentText(gender)
        self.input_tahun_masuk.setText(tahun_masuk)
        self.input_tgl_lahir.setDate(tanggal_lahir)
        self.input_status.setCurrentText(status)
        if dosen_wali_nama and dosen_wali_nama != "-":
            index = self.input_dosen_wali.findText(dosen_wali_nama)
            if index >= 0:
                self.input_dosen_wali.setCurrentIndex(index)
        else:
            self.input_dosen_wali.setCurrentIndex(0)

    def show_message(self, title, message):
        msg_box = QMessageBox()
        if title == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_text = f"<p style='font-size: 14px;'>{message}</p>"
        msg_box.setText(msg_text)
        msg_box.exec()

# ====================================================================
# --- KELAS: Halaman CRUD Dosen ---
# ====================================================================
class DosenWidget(QWidget):
    JABATAN_LIST = ["--Pilih Jabatan--", "Asisten Ahli", "Lektor", "Lektor Kepala", "Profesor"]

    def __init__(self):
        super().__init__()
        
        self.selected_dosen_id = None
        
        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.form_frame = QFrame() 
        self.form_frame.setObjectName("form_frame") 
        self.form_frame.setFixedWidth(380)
        self.form_frame.setEnabled(False) 
        form_layout = QFormLayout() 
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        self.input_nidn = QLineEdit()
        self.input_nama = QLineEdit()
        self.input_gender = QComboBox()
        self.input_gender.addItems(["L", "P"])
        self.input_jabatan = QComboBox()
        self.input_jabatan.addItems(self.JABATAN_LIST)
        self.input_email = QLineEdit()
        self.input_status = QComboBox()
        self.input_status.addItems(["Aktif", "Cuti", "Pensiun"])
        form_layout.addRow(QLabel("NIDN/NIP:"), self.input_nidn)
        form_layout.addRow(QLabel("Nama Lengkap:"), self.input_nama)
        form_layout.addRow(QLabel("Gender (L/P):"), self.input_gender)
        form_layout.addRow(QLabel("Jabatan Akademik:"), self.input_jabatan)
        form_layout.addRow(QLabel("Email:"), self.input_email)
        form_layout.addRow(QLabel("Status:"), self.input_status)
        btn_layout = QHBoxLayout()
        self.btn_update = QPushButton("Update Data") 
        self.btn_update.setObjectName("btn_simpan") 
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_hapus")
        self.btn_bersihkan = QPushButton("Bersihkan Form")
        self.btn_bersihkan.setObjectName("btn_bersihkan")
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_hapus)
        form_container_layout = QVBoxLayout(self.form_frame)
        form_container_layout.addLayout(form_layout)
        form_container_layout.addLayout(btn_layout)
        form_container_layout.addWidget(self.btn_bersihkan)
        main_layout.addWidget(self.form_frame) 

        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        button_bar_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import from Excel")
        self.btn_import.setObjectName("btn_simpan") 
        self.btn_import.setStyleSheet("font-weight: bold; padding: 10px;")
        self.btn_export = QPushButton("Export to Excel") 
        self.btn_export.setObjectName("btn_export") 
        self.btn_export.setStyleSheet("font-weight: bold; padding: 10px;")
        button_bar_layout.addWidget(self.btn_import)
        button_bar_layout.addWidget(self.btn_export) 
        button_bar_layout.addStretch() 
        table_layout.addLayout(button_bar_layout) 
        self.search_input = QLineEdit() 
        self.search_input.setPlaceholderText("Cari berdasarkan NIDN atau Nama...")
        table_layout.addWidget(self.search_input) 
        self.table_dsn = QTableWidget() 
        self.table_dsn.setColumnCount(8) 
        self.table_dsn.setHorizontalHeaderLabels([
            "#", "ID", "NIDN", "Nama", 
            "Gender", "Jabatan Akademik", "Email", "Status"
        ])
        self.table_dsn.verticalHeader().hide()
        self.table_dsn.setColumnHidden(1, True) 
        self.table_dsn.setColumnWidth(0, 50) 
        self.table_dsn.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) 
        self.table_dsn.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch) 
        self.table_dsn.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_dsn.setEditTriggers(QTableWidget.NoEditTriggers) 
        table_layout.addWidget(self.table_dsn)
        main_layout.addWidget(table_frame) 
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 3) 

        self.btn_update.clicked.connect(self.update_data) 
        self.btn_import.clicked.connect(self.import_from_excel) 
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_bersihkan.clicked.connect(self.clear_form)
        self.btn_hapus.clicked.connect(self.delete_data)
        self.table_dsn.itemClicked.connect(self.table_row_clicked) 
        self.search_input.textChanged.connect(self.filter_table)
        self.applyStyles()

    def applyStyles(self):
        self.setStyleSheet("""
            DosenWidget { background-color: #FFFFFF; }
            #form_frame {
                background-color: #F0F2F5;
                border-radius: 10px;
            }
            #form_frame QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QLineEdit, QDateEdit, QComboBox {
                font-size: 14px;
                background-color: #FFFFFF; 
                border: 1px solid #E0E0E0; 
                border-radius: 5px;
                padding: 8px;
                color: #000000; 
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            #form_frame QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            #btn_simpan { background-color: #0078D7; }
            #btn_simpan:hover { background-color: #005A9E; }
            #btn_simpan:pressed { background-color: #004A8C; }
            #btn_export {
                background-color: #6C757D;
            }
            #btn_export:hover { background-color: #5A6268; }
            #btn_export:pressed { background-color: #4E555B; }
            #btn_hapus { background-color: #D9534F; }
            #btn_hapus:hover { background-color: #C9302C; }
            #btn_hapus:pressed { background-color: #AC2925; }
            #btn_bersihkan { background-color: #6C757D; }
            #btn_bersihkan:hover { background-color: #5A6268; }
            #btn_bersihkan:pressed { background-color: #4E555B; }
            QTableWidget {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F7F7F7; 
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QFrame {
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                selection-background-color: #0078D7; 
                selection-color: #FFFFFF; 
                outline: 0px; 
            }
            QCalendarWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
            }
            QCalendarWidget QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
            }
            QCalendarWidget QTableView QHeaderView::section {
                background-color: #F7F7F7;
                color: #000000; 
                font-weight: 600;
            }
            QCalendarWidget QToolButton {
                color: #000000; 
                background-color: #F7F7F7;
                border: none;
            }
            QCalendarWidget QMenu {
                background-color: #FFFFFF;
                color: #000000; 
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #0078D7;
            }
        """)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table_dsn.rowCount()):
            nidn_item = self.table_dsn.item(row, 2)  
            nama_item = self.table_dsn.item(row, 3) 
            if nidn_item and nama_item:
                nidn_text = nidn_item.text().lower()
                nama_text = nama_item.text().lower()
                if search_text in nidn_text or search_text in nama_text:
                    self.table_dsn.setRowHidden(row, False)
                else:
                    self.table_dsn.setRowHidden(row, True)
    
    def load_data(self):
        print("Memuat data dosen...")
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            semua_dosen = db_session.query(Dosen).all()
            self.table_dsn.setRowCount(0) 
            for row_position, dsn in enumerate(semua_dosen):
                self.table_dsn.insertRow(row_position)
                nomor_item = QTableWidgetItem(str(row_position + 1))
                nomor_item.setTextAlignment(Qt.AlignCenter)
                self.table_dsn.setItem(row_position, 0, nomor_item) # '#'
                self.table_dsn.setItem(row_position, 1, QTableWidgetItem(str(dsn.id))) # ID
                self.table_dsn.setItem(row_position, 2, QTableWidgetItem(dsn.nidn)) # NIDN
                self.table_dsn.setItem(row_position, 3, QTableWidgetItem(dsn.nama)) # Nama
                self.table_dsn.setItem(row_position, 4, QTableWidgetItem(dsn.gender)) # Gender
                self.table_dsn.setItem(row_position, 5, QTableWidgetItem(dsn.jabatan_akademik)) # Jabatan
                self.table_dsn.setItem(row_position, 6, QTableWidgetItem(dsn.email)) # Email
                self.table_dsn.setItem(row_position, 7, QTableWidgetItem(dsn.status)) # Status
        except Exception as e:
            self.show_message("Error", f"Gagal memuat data dosen: {e}")
        finally:
            db_session.close()

    def update_data(self):
        if not self.selected_dosen_id:
            self.show_message("Error", "Pilih data dari tabel yang ingin Anda update.")
            return
        nidn = self.input_nidn.text()
        nama = self.input_nama.text()
        gender = self.input_gender.currentText()
        jabatan = self.input_jabatan.currentText()
        email = self.input_email.text()
        status = self.input_status.currentText()
        if not nidn or not nama or not email:
            self.show_message("Error", "NIDN, Nama, dan Email tidak boleh kosong.")
            return
        if jabatan == "--Pilih Jabatan--":
            self.show_message("Error", "Silakan pilih Jabatan.")
            return
            
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            dsn = db_session.query(Dosen).get(self.selected_dosen_id)
            if dsn:
                if dsn.nidn != nidn:
                    nidn_ada = db_session.query(Dosen).filter_by(nidn=nidn).first()
                    if nidn_ada:
                        self.show_message("Error", f"NIDN {nidn} sudah terdaftar.")
                        db_session.rollback()
                        return
                if dsn.email != email:
                    email_ada = db_session.query(Dosen).filter_by(email=email).first()
                    if email_ada:
                        self.show_message("Error", f"Email {email} sudah terdaftar.")
                        db_session.rollback()
                        return
                dsn.nidn = nidn
                dsn.nama = nama
                dsn.gender = gender
                dsn.jabatan_akademik = jabatan
                dsn.email = email
                dsn.status = status
                self.show_message("Sukses", f"Data {nama} berhasil diperbarui.")
                db_session.commit()
            else:
                self.show_message("Error", "Data tidak ditemukan (mungkin sudah dihapus).")
        except Exception as e:
            db_session.rollback()
            self.show_message("Error", f"Gagal menyimpan data: {e}")
        finally:
            db_session.close()
        self.load_data()
        self.clear_form()

    def import_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        try:
            df = pd.read_excel(file_path)
            df = df.astype(str)
        except Exception as e:
            self.show_message("Error", f"Gagal membaca file Excel: {e}")
            return
        required_columns = [
            "NIDN", "Nama", "Gender", 
            "Jabatan Akademik", "Email", "Status"
        ]
        if not all(col in df.columns for col in required_columns):
            self.show_message("Error", 
                "Format Excel salah.\nPastikan Anda memiliki kolom:\n" +
                ", ".join(required_columns)
            )
            return
            
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        added_count = 0
        skipped_count = 0
        try:
            for index, row in df.iterrows():
                nidn = row["NIDN"]
                email = row["Email"]
                jabatan_excel = row["Jabatan Akademik"]
                data_ada = db_session.query(Dosen).filter(
                    (Dosen.nidn == nidn) | (Dosen.email == email)
                ).first()
                if data_ada:
                    skipped_count += 1
                    continue
                if jabatan_excel not in self.JABATAN_LIST:
                    skipped_count += 1
                    continue
                gender = str(row["Gender"]).upper()
                if gender not in ['L', 'P']:
                    skipped_count += 1
                    continue
                dsn_baru = Dosen(
                    nidn=nidn,
                    nama=row["Nama"],
                    gender=gender,
                    jabatan_akademik=jabatan_excel,
                    email=email,
                    status=row["Status"]
                )
                db_session.add(dsn_baru)
                added_count += 1
            db_session.commit()
            self.show_message("Sukses", 
                f"Import Selesai.\n\n"
                f"Data baru ditambahkan: {added_count}\n"
                f"Data duplikat/salah format dilewati: {skipped_count}"
            )
        except Exception as e:
            db_session.rollback()
            self.show_message("Error", f"Terjadi error saat import: {e}")
        finally:
            db_session.close()
        self.load_data()

    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan File Excel",
            "export_dosen.xlsx", 
            "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        data_to_export = []
        headers = []
        for col in range(self.table_dsn.columnCount()):
            if not self.table_dsn.isColumnHidden(col):
                headers.append(self.table_dsn.horizontalHeaderItem(col).text())
        for row in range(self.table_dsn.rowCount()):
            if not self.table_dsn.isRowHidden(row):
                row_data = []
                for col in range(self.table_dsn.columnCount()):
                    if not self.table_dsn.isColumnHidden(col):
                        item = self.table_dsn.item(row, col)
                        row_data.append(item.text() if item else "")
                data_to_export.append(row_data)
        try:
            df = pd.DataFrame(data_to_export, columns=headers)
            df.to_excel(file_path, index=False)
            self.show_message("Sukses", f"Data berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            self.show_message("Error", f"Gagal mengekspor file: {e}")

    def delete_data(self):
        if not self.selected_dosen_id:
            self.show_message("Error", "Pilih data dari tabel yang ingin dihapus.")
            return
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"<p style='font-size: 14px;'>Apakah Anda yakin ingin menghapus data dengan ID {self.selected_dosen_id}?</p>")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        if msg_box.exec() == QMessageBox.Yes:
            if 'SessionLocal' not in globals():
                self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
                return
                
            db_session = SessionLocal()
            try:
                dsn = db_session.query(Dosen).get(self.selected_dosen_id)
                if dsn:
                    db_session.delete(dsn)
                    db_session.commit()
                    self.show_message("Sukses", "Data berhasil dihapus.")
                else:
                    self.show_message("Error", "Data tidak ditemukan.")
            except Exception as e:
                db_session.rollback()
                self.show_message("Error", f"Gagal menghapus data: {e}")
            finally:
                db_session.close()
            self.load_data()
            self.clear_form()

    def clear_form(self):
        self.selected_dosen_id = None 
        self.input_nidn.clear()
        self.input_nama.clear()
        self.input_gender.setCurrentIndex(0) 
        self.input_jabatan.setCurrentIndex(0)
        self.input_email.clear()
        self.input_status.setCurrentIndex(0)
        self.input_dosen_wali.setCurrentIndex(0)
        self.form_frame.setEnabled(False) 
        self.input_nidn.setReadOnly(False) 

    def table_row_clicked(self, item):
        self.form_frame.setEnabled(True) 
        self.input_nidn.setReadOnly(False) 
        row = item.row()
        dsn_id = int(self.table_dsn.item(row, 1).text())
        nidn = self.table_dsn.item(row, 2).text()
        nama = self.table_dsn.item(row, 3).text()
        gender = self.table_dsn.item(row, 4).text() 
        jabatan = self.table_dsn.item(row, 5).text() 
        email = self.table_dsn.item(row, 6).text()
        status = self.table_dsn.item(row, 7).text()
        self.selected_dosen_id = dsn_id
        self.input_nidn.setText(nidn)
        self.input_nama.setText(nama)
        self.input_gender.setCurrentText(gender)
        self.input_jabatan.setCurrentText(jabatan)
        self.input_email.setText(email)
        self.input_status.setCurrentText(status)

    def show_message(self, title, message):
        msg_box = QMessageBox()
        if title == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_text = f"<p style='font-size: 14px;'>{message}</p>"
        msg_box.setText(msg_text)
        msg_box.exec()
# ====================================================================
# --- KELAS: Halaman CRUD Pengguna ---
# ====================================================================
class PenggunaWidget(QWidget):
    ROLE_LIST = ["Admin Akademik", "Kepala Jurusan", "Rektor", "Admin Manajemen"]
    
    def __init__(self, current_username): 
        super().__init__()
        
        self.selected_pengguna_id = None
        self.current_username = current_username 
        
        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.form_frame = QFrame() 
        self.form_frame.setObjectName("form_frame") 
        form_layout = QFormLayout() 
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Wajib diisi untuk pengguna baru")
        self.input_role = QComboBox()
        self.input_role.addItems(self.ROLE_LIST)
        form_layout.addRow(QLabel("Username:"), self.input_username)
        form_layout.addRow(QLabel("Password:"), self.input_password)
        form_layout.addRow(QLabel("Role:"), self.input_role)
        btn_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan") 
        self.btn_simpan.setObjectName("btn_simpan") 
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_hapus")
        self.btn_bersihkan = QPushButton("Bersihkan Form")
        self.btn_bersihkan.setObjectName("btn_bersihkan")
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_hapus)
        form_container_layout = QVBoxLayout(self.form_frame)
        form_container_layout.addLayout(form_layout)
        form_container_layout.addLayout(btn_layout)
        form_container_layout.addWidget(self.btn_bersihkan)
        form_container_layout.addStretch() 
        main_layout.addWidget(self.form_frame) 

        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        self.search_input = QLineEdit() 
        self.search_input.setPlaceholderText("Cari berdasarkan Username atau Role...")
        table_layout.addWidget(self.search_input) 
        self.table_pengguna = QTableWidget() 
        self.table_pengguna.setColumnCount(4) 
        self.table_pengguna.setHorizontalHeaderLabels([
            "#", "ID", "Username", "Role"
        ])
        self.table_pengguna.verticalHeader().hide()
        self.table_pengguna.setColumnHidden(1, True) 
        self.table_pengguna.setColumnWidth(0, 50) 
        self.table_pengguna.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) 
        self.table_pengguna.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) 
        self.table_pengguna.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_pengguna.setEditTriggers(QTableWidget.NoEditTriggers) 
        table_layout.addWidget(self.table_pengguna)
        main_layout.addWidget(table_frame) 
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 2) 

        self.btn_simpan.clicked.connect(self.save_data) 
        self.btn_bersihkan.clicked.connect(self.clear_form)
        self.btn_hapus.clicked.connect(self.delete_data)
        self.table_pengguna.itemClicked.connect(self.table_row_clicked) 
        self.search_input.textChanged.connect(self.filter_table)
        self.applyStyles()

    def applyStyles(self):
        self.setStyleSheet("""
            PenggunaWidget { background-color: #FFFFFF; }
            #form_frame {
                background-color: #F0F2F5;
                border-radius: 10px;
            }
            #form_frame QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QLineEdit, QDateEdit, QComboBox {
                font-size: 14px;
                background-color: #FFFFFF; 
                border: 1px solid #E0E0E0; 
                border-radius: 5px;
                padding: 8px;
                color: #000000; 
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            #form_frame QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            #btn_simpan { background-color: #0078D7; }
            #btn_simpan:hover { background-color: #005A9E; }
            #btn_simpan:pressed { background-color: #004A8C; }
            #btn_hapus { background-color: #D9534F; }
            #btn_hapus:hover { background-color: #C9302C; }
            #btn_hapus:pressed { background-color: #AC2925; }
            #btn_bersihkan { background-color: #6C757D; }
            #btn_bersihkan:hover { background-color: #5A6268; }
            #btn_bersihkan:pressed { background-color: #4E555B; }
            QTableWidget {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F7F7F7; 
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QFrame {
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                selection-background-color: #0078D7; 
                selection-color: #FFFFFF; 
                outline: 0px; 
            }
        """)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table_pengguna.rowCount()):
            username_item = self.table_pengguna.item(row, 2)  
            role_item = self.table_pengguna.item(row, 3) 
            if username_item and role_item:
                username_text = username_item.text().lower()
                role_text = role_item.text().lower()
                if search_text in username_text or search_text in role_text:
                    self.table_pengguna.setRowHidden(row, False)
                else:
                    self.table_pengguna.setRowHidden(row, True)
    
    def load_data(self):
        print("Memuat data pengguna...")
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            semua_pengguna = db_session.query(Pengguna).all()
            self.table_pengguna.setRowCount(0) 
            for row_position, user in enumerate(semua_pengguna):
                self.table_pengguna.insertRow(row_position)
                nomor_item = QTableWidgetItem(str(row_position + 1))
                nomor_item.setTextAlignment(Qt.AlignCenter)
                self.table_pengguna.setItem(row_position, 0, nomor_item) # '#'
                self.table_pengguna.setItem(row_position, 1, QTableWidgetItem(str(user.id))) # ID
                self.table_pengguna.setItem(row_position, 2, QTableWidgetItem(user.username)) # Username
                self.table_pengguna.setItem(row_position, 3, QTableWidgetItem(user.role)) # Role
        except Exception as e:
            self.show_message("Error", f"Gagal memuat data pengguna: {e}")
        finally:
            db_session.close()

    def save_data(self):
        username = self.input_username.text()
        password = self.input_password.text() 
        role = self.input_role.currentText()
        if not username:
            self.show_message("Error", "Username tidak boleh kosong.")
            return
            
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            if self.selected_pengguna_id:
                user = db_session.query(Pengguna).get(self.selected_pengguna_id)
                if user:
                    if user.username != username:
                        username_ada = db_session.query(Pengguna).filter_by(username=username).first()
                        if username_ada:
                            self.show_message("Error", f"Username '{username}' sudah terdaftar.")
                            db_session.rollback()
                            return
                    if password:
                        password_bytes = password.encode('utf-8')
                        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                        user.hashed_password = hashed_password.decode('utf-8')
                    user.username = username
                    user.role = role
                    self.show_message("Sukses", f"Data pengguna '{username}' berhasil diperbarui.")
            else:
                if not password:
                    self.show_message("Error", "Password wajib diisi untuk pengguna baru.")
                    return
                username_ada = db_session.query(Pengguna).filter_by(username=username).first()
                if username_ada:
                    self.show_message("Error", f"Username '{username}' sudah terdaftar.")
                    return
                password_bytes = password.encode('utf-8')
                hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                user_baru = Pengguna(
                    username=username,
                    hashed_password=hashed_password.decode('utf-8'),
                    role=role
                )
                db_session.add(user_baru)
                self.show_message("Sukses", f"Pengguna '{username}' berhasil dibuat.")
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.show_message("Error", f"Gagal menyimpan data: {e}")
        finally:
            db_session.close()
        self.load_data()
        self.clear_form()

    def delete_data(self):
        if not self.selected_pengguna_id:
            self.show_message("Error", "Pilih pengguna dari tabel yang ingin dihapus.")
            return
        selected_row = self.table_pengguna.currentRow()
        username_to_delete = self.table_pengguna.item(selected_row, 2).text()
        if username_to_delete == "admin":
            self.show_message("Error", "Akun 'admin' utama tidak boleh dihapus.")
            return
        if username_to_delete == self.current_username:
            self.show_message("Error", "Anda tidak dapat menghapus akun Anda sendiri.")
            return
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"<p style='font-size: 14px;'>Apakah Anda yakin ingin menghapus pengguna '{username_to_delete}'?</p>")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        if msg_box.exec() == QMessageBox.Yes:
            if 'SessionLocal' not in globals():
                self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
                return
                
            db_session = SessionLocal()
            try:
                user = db_session.query(Pengguna).get(self.selected_pengguna_id)
                if user:
                    db_session.delete(user)
                    db_session.commit()
                    self.show_message("Sukses", f"Pengguna '{username_to_delete}' berhasil dihapus.")
                else:
                    self.show_message("Error", "Data tidak ditemukan.")
            except Exception as e:
                db_session.rollback()
                self.show_message("Error", f"Gagal menghapus data: {e}")
            finally:
                db_session.close()
            self.load_data()
            self.clear_form()

    def clear_form(self):
        self.selected_pengguna_id = None 
        self.input_username.clear()
        self.input_password.clear()
        self.input_role.setCurrentIndex(0) 
        self.input_username.setReadOnly(False)
        self.input_password.setPlaceholderText("Wajib diisi untuk pengguna baru")

    def table_row_clicked(self, item):
        row = item.row()
        user_id = int(self.table_pengguna.item(row, 1).text())
        username = self.table_pengguna.item(row, 2).text()
        role = self.table_pengguna.item(row, 3).text()
        self.selected_pengguna_id = user_id
        self.input_username.setText(username)
        self.input_role.setCurrentText(role)
        self.input_password.clear()
        self.input_password.setPlaceholderText("Biarkan kosong untuk menjaga password lama")
        if username == "admin":
            self.input_username.setReadOnly(True)
        else:
            self.input_username.setReadOnly(False)

    def show_message(self, title, message):
        msg_box = QMessageBox()
        if title == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_text = f"<p style='font-size: 14px;'>{message}</p>"
        msg_box.setText(msg_text)
        msg_box.exec()


# ====================================================================
# --- KELAS: Halaman CRUD Matakuliah ---
# ====================================================================
class MatakuliahWidget(QWidget):
    PRODI_LIST = ["--Pilih Prodi--"]

    def __init__(self):
        super().__init__()
        self.selected_matakuliah_id = None
        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.form_frame = QFrame() 
        self.form_frame.setObjectName("form_frame") 
        self.form_frame.setEnabled(False) 
        form_layout = QFormLayout() 
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        self.input_kode_mk = QLineEdit()
        self.input_nama_mk = QLineEdit()
        self.input_sks = QLineEdit()
        self.input_sks.setValidator(QIntValidator(1, 9)) 
        self.input_semester = QLineEdit()
        self.input_semester.setValidator(QIntValidator(1, 8)) 
        self.input_prodi = QComboBox()
        self.input_prodi.addItems(self.PRODI_LIST)

        form_layout.addRow(QLabel("Kode MK:"), self.input_kode_mk)
        form_layout.addRow(QLabel("Nama Matakuliah:"), self.input_nama_mk)
        form_layout.addRow(QLabel("SKS:"), self.input_sks)
        form_layout.addRow(QLabel("Semester:"), self.input_semester)
        form_layout.addRow(QLabel("Program Studi:"), self.input_prodi)
        
        btn_layout = QHBoxLayout()
        self.btn_update = QPushButton("Update Data") 
        self.btn_update.setObjectName("btn_simpan") 
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_hapus")
        self.btn_bersihkan = QPushButton("Bersihkan Form")
        self.btn_bersihkan.setObjectName("btn_bersihkan")
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_hapus)
        form_container_layout = QVBoxLayout(self.form_frame)
        form_container_layout.addLayout(form_layout)
        form_container_layout.addLayout(btn_layout)
        form_container_layout.addWidget(self.btn_bersihkan)
        form_container_layout.addStretch() 
        main_layout.addWidget(self.form_frame) 

        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        button_bar_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import from Excel")
        self.btn_import.setObjectName("btn_simpan") 
        self.btn_import.setStyleSheet("font-weight: bold; padding: 10px;")
        self.btn_export = QPushButton("Export to Excel") 
        self.btn_export.setObjectName("btn_export") 
        self.btn_export.setStyleSheet("font-weight: bold; padding: 10px;")
        button_bar_layout.addWidget(self.btn_import)
        button_bar_layout.addWidget(self.btn_export) 
        button_bar_layout.addStretch() 
        table_layout.addLayout(button_bar_layout) 
        
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit() 
        self.search_input.setPlaceholderText("Cari Kode MK atau Nama...")
        filter_layout.addWidget(self.search_input, 2) 
        self.filter_prodi = QComboBox()
        self.filter_prodi.addItems(["Semua Prodi"] + self.PRODI_LIST[1:])
        filter_layout.addWidget(self.filter_prodi, 1) 
        self.filter_semester = QComboBox()
        self.filter_semester.addItems(["Semua Semester", "1", "2", "3", "4", "5", "6", "7", "8"])
        filter_layout.addWidget(self.filter_semester, 1) 
        table_layout.addLayout(filter_layout) 
        
        self.table_mk = QTableWidget() 
        self.table_mk.setColumnCount(7) 
        self.table_mk.setHorizontalHeaderLabels([
            "#", "ID", "Kode MK", "Nama Matakuliah", "SKS", 
            "Semester", "Program Studi"
        ])
        self.table_mk.verticalHeader().hide()
        self.table_mk.setColumnHidden(1, True) 
        self.table_mk.setColumnWidth(0, 50) 
        self.table_mk.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) 
        self.table_mk.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch) 
        self.table_mk.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_mk.setEditTriggers(QTableWidget.NoEditTriggers) 
        table_layout.addWidget(self.table_mk)
        main_layout.addWidget(table_frame) 
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 2) 

        self.btn_update.clicked.connect(self.update_data) 
        self.btn_import.clicked.connect(self.import_from_excel) 
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_bersihkan.clicked.connect(self.clear_form)
        self.btn_hapus.clicked.connect(self.delete_data)
        self.table_mk.itemClicked.connect(self.table_row_clicked) 
        self.search_input.textChanged.connect(self.filter_table)
        self.filter_prodi.currentTextChanged.connect(self.filter_table)
        self.filter_semester.currentTextChanged.connect(self.filter_table)
        self.applyStyles() 

    def applyStyles(self):
        self.setStyleSheet("""
            MatakuliahWidget { background-color: #FFFFFF; }
            #form_frame {
                background-color: #F0F2F5;
                border-radius: 10px;
            }
            #form_frame QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QLineEdit, QDateEdit, QComboBox {
                font-size: 14px;
                background-color: #FFFFFF; 
                border: 1px solid #E0E0E0; 
                border-radius: 5px;
                padding: 8px;
                color: #000000; 
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            #form_frame QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            #btn_simpan { background-color: #0078D7; }
            #btn_simpan:hover { background-color: #005A9E; }
            #btn_simpan:pressed { background-color: #004A8C; }
            #btn_export {
                background-color: #6C757D;
            }
            #btn_export:hover { background-color: #5A6268; }
            #btn_export:pressed { background-color: #4E555B; }
            #btn_hapus { background-color: #D9534F; }
            #btn_hapus:hover { background-color: #C9302C; }
            #btn_hapus:pressed { background-color: #AC2925; }
            #btn_bersihkan { background-color: #6C757D; }
            #btn_bersihkan:hover { background-color: #5A6268; }
            #btn_bersihkan:pressed { background-color: #4E555B; }
            QTableWidget {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F7F7F7; 
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QFrame {
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                selection-background-color: #0078D7; 
                selection-color: #FFFFFF; 
                outline: 0px; 
            }
        """)

    def filter_table(self):
        txt, fp, fs = self.search_input.text().lower(), self.filter_prodi.currentText(), self.filter_semester.currentText()
        for r in range(self.table_mk.rowCount()):
            k, n, s, p = [self.table_mk.item(r, i).text().lower() if self.table_mk.item(r, i) else "" for i in [2,3,5,6]]
            match = (txt in k or txt in n) and (fp == "Semua Prodi" or fp.lower() == p) and (fs == "Semua Semester" or fs == s)
            self.table_mk.setRowHidden(r, not match)
    
    def load_data(self):
        if 'SessionLocal' not in globals(): return
        db = SessionLocal()
        try:
            prodi_query = db.query(Mahasiswa.program_studi.distinct()).order_by(Mahasiswa.program_studi).all()
            self.PRODI_LIST = ["--Pilih Prodi--"] + [p[0] for p in prodi_query if p[0]]
            
            cur_filt, cur_inp = self.filter_prodi.currentText(), self.input_prodi.currentText()
            
            self.filter_prodi.clear(); self.filter_prodi.addItems(["Semua Prodi"] + self.PRODI_LIST[1:])
            self.input_prodi.clear(); self.input_prodi.addItems(self.PRODI_LIST)
            
            self.filter_prodi.setCurrentText(cur_filt)
            self.input_prodi.setCurrentText(cur_inp)

            self.table_mk.setRowCount(0) 
            for r, mk in enumerate(db.query(Matakuliah).all()):
                self.table_mk.insertRow(r)
                self.table_mk.setItem(r, 0, QTableWidgetItem(str(r+1)))
                self.table_mk.item(r,0).setTextAlignment(Qt.AlignCenter)
                for i, val in enumerate([mk.id, mk.kode_mk, mk.nama_matakuliah, mk.sks, mk.semester, mk.program_studi], 1):
                    self.table_mk.setItem(r, i, QTableWidgetItem(str(val)))
        except Exception as e:
            self.show_message("Error", f"Gagal load data: {e}")
        finally:
            db.close()

    def update_data(self):
        if not self.selected_matakuliah_id: return self.show_message("Error", "Pilih matakuliah.")
        kode, nama, prodi = self.input_kode_mk.text(), self.input_nama_mk.text(), self.input_prodi.currentText()
        try: sks, sem = int(self.input_sks.text()), int(self.input_semester.text())
        except: return self.show_message("Error", "SKS/Semester harus angka.")
        
        if not all([kode, nama]) or prodi == "--Pilih Prodi--": 
            return self.show_message("Error", "Data tidak lengkap (pilih Program Studi).")
            
        if 'SessionLocal' not in globals(): return
        db = SessionLocal()
        try:
            mk = db.query(Matakuliah).get(self.selected_matakuliah_id)
            if mk:
                if mk.kode_mk != kode and db.query(Matakuliah).filter_by(kode_mk=kode).first(): 
                    return self.show_message("Error", "Kode MK sudah ada.")
                mk.kode_mk, mk.nama_matakuliah, mk.sks, mk.semester, mk.program_studi = kode, nama, sks, sem, prodi
                db.commit()
                self.show_message("Sukses", "Data diupdate.")
        except Exception as e:
            db.rollback(); self.show_message("Error", f"Gagal update: {e}")
        finally:
            db.close()
        self.load_data(); self.clear_form()

    def import_from_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Excel", "", "Excel Files (*.xlsx *.xls)")
        
        if not path: 
            return
        try:
            df = pd.read_excel(path).astype(str)
            req = ["Kode MK", "Nama Matakuliah", "SKS", "Semester", "Program Studi"]
            if not all(c in df.columns for c in req): 
                if "Fakultas" in df.columns and "Program Studi" not in df.columns:
                    df.rename(columns={"Fakultas": "Program Studi"}, inplace=True)
                else:
                    raise ValueError("Kolom Excel tidak sesuai. Pastikan ada kolom: " + ", ".join(req))
            db = SessionLocal()
            add = 0 
            for _, row in df.iterrows():
                prodi_valid = (len(self.PRODI_LIST) <= 1) or (row["Program Studi"] in self.PRODI_LIST)
                kode_mk_exists = db.query(Matakuliah).filter_by(kode_mk=row["Kode MK"]).first()
                if not kode_mk_exists and prodi_valid:
                    try: 
                        db.add(Matakuliah(
                            kode_mk=row["Kode MK"], 
                            nama_matakuliah=row["Nama Matakuliah"], 
                            sks=int(row["SKS"]),             
                            semester=int(row["Semester"]),  
                            program_studi=row["Program Studi"]
                        ))
                        add += 1 
                    except Exception: 
                        pass 
            
            
            db.commit()
            self.show_message("Sukses", f"Import selesai. Berhasil menambah: {add} data baru.")
            
        except Exception as e:
            
            self.show_message("Error", f"Gagal import data: {e}")
            if 'db' in locals(): db.rollback()
            
        finally:
            if 'db' in locals(): db.close()
            
        self.load_data()


    def export_to_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan Excel", "export_mk.xlsx", "Excel (*.xlsx)")
        if not path: return
        try:
            data = [[self.table_mk.item(r, c).text() for c in range(self.table_mk.columnCount()) if not self.table_mk.isColumnHidden(c)] for r in range(self.table_mk.rowCount()) if not self.table_mk.isRowHidden(r)]
            cols = [self.table_mk.horizontalHeaderItem(c).text() for c in range(self.table_mk.columnCount()) if not self.table_mk.isColumnHidden(c)]
            pd.DataFrame(data, columns=cols).to_excel(path, index=False)
            self.show_message("Sukses", f"Diekspor ke {path}")
        except Exception as e: self.show_message("Error", f"Gagal ekspor: {e}")

    def delete_data(self):
        if self.selected_matakuliah_id and QMessageBox.question(self, "Hapus", "Yakin hapus?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                db.delete(db.query(Matakuliah).get(self.selected_matakuliah_id))
                db.commit()
                self.show_message("Sukses", "Dihapus.")
            finally:
                db.close()
            self.load_data(); self.clear_form()

    def clear_form(self):
        self.selected_matakuliah_id = None 
        for w in [self.input_kode_mk, self.input_nama_mk, self.input_sks, self.input_semester]: w.clear()
        self.input_prodi.setCurrentIndex(0) 
        self.form_frame.setEnabled(False) 
        self.input_kode_mk.setReadOnly(False) 

    def table_row_clicked(self, item):
        self.form_frame.setEnabled(True) 
        self.input_kode_mk.setReadOnly(False) 
        r = item.row()
        self.selected_matakuliah_id = int(self.table_mk.item(r, 1).text())
        self.input_kode_mk.setText(self.table_mk.item(r, 2).text())
        self.input_nama_mk.setText(self.table_mk.item(r, 3).text())
        self.input_sks.setText(self.table_mk.item(r, 4).text())
        self.input_semester.setText(self.table_mk.item(r, 5).text())
        self.input_prodi.setCurrentText(self.table_mk.item(r, 6).text())

    def show_message(self, title, message):
        msg_box = QMessageBox()
        if title == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_text = f"<p style='font-size: 14px;'>{message}</p>"
        msg_box.setText(msg_text)
        msg_box.exec()

# ====================================================================
# --- KELAS: Halaman Manajemen Nilai ---
# ====================================================================
class NilaiWidget(QWidget):
    
    NILAI_BOBOT_MAP = {
        "A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0
    }
    NILAI_HURUF_LIST = ["A", "B", "C", "D", "E"]

    def __init__(self):
        super().__init__()
        
        self.mahasiswa_map = {} 
        self.matakuliah_map = {} 
        self.all_matakuliah_map = defaultdict(list)
        self.prodi_list = [] 
        self.current_mahasiswa_id = None
        self.current_mahasiswa_sks = 0
        self.current_mahasiswa_ipk = 0.0
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        top_frame = QFrame()
        top_frame.setObjectName("form_frame") 
        top_layout = QHBoxLayout(top_frame)
        
        top_layout.addWidget(QLabel("Pilih Mahasiswa:"))
        
        self.mhs_combo = QComboBox()
        self.mhs_combo.setEditable(True)
        self.mhs_combo.setInsertPolicy(QComboBox.NoInsert)
        self.mhs_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.mhs_combo.completer().setFilterMode(Qt.MatchContains)
        
        top_layout.addWidget(self.mhs_combo, 2) 
        
        self.ipk_label = QLabel("IPK: -")
        self.ipk_label.setObjectName("ipk_label")
        self.ipk_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_layout.addWidget(self.ipk_label, 1) 
        
        main_layout.addWidget(top_frame)

        self.tambah_nilai_frame = QFrame()
        self.tambah_nilai_frame.setObjectName("form_frame")
        self.tambah_nilai_frame.setEnabled(False) 
        
        tambah_layout = QHBoxLayout(self.tambah_nilai_frame)
        tambah_layout.setContentsMargins(10, 10, 10, 10)
        
        tambah_layout.addWidget(QLabel("Tambah Nilai:"))
        
        self.prodi_combo = QComboBox()
        self.prodi_combo.setObjectName("prodi_display_box")
        self.prodi_combo.setEnabled(False) 
        tambah_layout.addWidget(self.prodi_combo, 2) 

        self.semester_combo = QComboBox()
        self.semester_combo.addItems(["-- Pilih Semester --", "1", "2", "3", "4", "5", "6", "7", "8"])
        self.semester_combo.setEnabled(False) 
        tambah_layout.addWidget(self.semester_combo, 1) 

        self.mk_combo = QComboBox()
        self.mk_combo.setEditable(True)
        self.mk_combo.setInsertPolicy(QComboBox.NoInsert)
        self.mk_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.mk_combo.completer().setFilterMode(Qt.MatchContains)
        self.mk_combo.setEnabled(False) 
        tambah_layout.addWidget(self.mk_combo, 3) 
        
        self.nilai_combo = QComboBox()
        self.nilai_combo.addItems(self.NILAI_HURUF_LIST)
        tambah_layout.addWidget(self.nilai_combo, 1) 
        
        self.btn_simpan_nilai = QPushButton("Simpan Nilai")
        self.btn_simpan_nilai.setObjectName("btn_simpan")
        tambah_layout.addWidget(self.btn_simpan_nilai, 1) 
        
        main_layout.addWidget(self.tambah_nilai_frame)

        transkrip_frame = QFrame()
        transkrip_layout = QVBoxLayout(transkrip_frame)
        
        self.table_nilai = QTableWidget()
        self.table_nilai.setColumnCount(8)
        self.table_nilai.setHorizontalHeaderLabels([
            "#", "ID Nilai", "Kode MK", "Nama Matakuliah", 
            "SKS", "Nilai", "Bobot", "Semester"
        ])
        self.table_nilai.verticalHeader().hide()
        self.table_nilai.setColumnHidden(1, True) 
        self.table_nilai.setColumnWidth(0, 50)
        self.table_nilai.setColumnWidth(4, 50) 
        self.table_nilai.setColumnWidth(5, 50) 
        self.table_nilai.setColumnWidth(6, 50) 
        self.table_nilai.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) 
        self.table_nilai.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_nilai.setEditTriggers(QTableWidget.NoEditTriggers)
        
        transkrip_layout.addWidget(self.table_nilai)
        
        self.btn_hapus_nilai = QPushButton("Hapus Nilai Terpilih")
        self.btn_hapus_nilai.setObjectName("btn_hapus")
        transkrip_layout.addWidget(self.btn_hapus_nilai)
        
        main_layout.addWidget(transkrip_frame)
        
        self.mhs_combo.activated.connect(self.mahasiswa_dipilih)
        self.semester_combo.activated.connect(self.update_mk_dropdown)
        self.btn_simpan_nilai.clicked.connect(self.simpan_nilai_baru)
        self.btn_hapus_nilai.clicked.connect(self.hapus_nilai)
        
        self.applyStyles()

    def applyStyles(self):
        self.setStyleSheet("""
            NilaiWidget { background-color: #FFFFFF; }
            #form_frame {
                background-color: #F0F2F5;
                border-radius: 10px;
                padding: 10px;
            }
            #form_frame QLabel, #ipk_label {
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QLineEdit, QDateEdit, QComboBox {
                font-size: 14px;
                background-color: #FFFFFF; 
                border: 1px solid #E0E0E0; 
                border-radius: 5px;
                padding: 8px;
                color: #000000; 
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            #btn_simpan { background-color: #0078D7; }
            #btn_simpan:hover { background-color: #005A9E; }
            #btn_simpan:pressed { background-color: #004A8C; }
            #btn_hapus { background-color: #D9534F; }
            #btn_hapus:hover { background-color: #C9302C; }
            #btn_hapus:pressed { background-color: #AC2925; }
            QTableWidget {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F7F7F7; 
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-size: 14px;
                font-weight: 600;
                color: #000000; 
            }
            QFrame {
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                color: #000000; 
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                selection-background-color: #0078D7; 
                selection-color: #FFFFFF; 
                outline: 0px; 
            }
            
            QComboBox#prodi_display_box {
                color: #000000; 
                padding-right: 8px; 
            }
            QComboBox#prodi_display_box::drop-down {
                border: 0px;
                width: 0px;
            }
        """)

    def load_initial_data(self):
        print("Memuat data awal Manajemen Nilai...")
        
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            semua_mahasiswa = db_session.query(Mahasiswa).filter_by(status='Aktif').all()
            self.mahasiswa_map.clear()
            self.mhs_combo.clear()
            
            model = QStandardItemModel()
            model.appendRow(QStandardItem("-- Pilih Mahasiswa --"))
            
            for mhs in semua_mahasiswa:
                display_text = f"{mhs.nama} ({mhs.nim})"
                self.mahasiswa_map[display_text] = {"id": mhs.id, "prodi": mhs.program_studi}
                
                item = QStandardItem(display_text)
                model.appendRow(item)
                
            self.mhs_combo.setModel(model)
            self.mhs_combo.setModelColumn(0)

            prodi_query = db_session.query(Mahasiswa.program_studi.distinct()).order_by(Mahasiswa.program_studi).all()
            self.prodi_list = ["-- Pilih Prodi --"] + [p[0] for p in prodi_query if p[0]]
            self.prodi_combo.clear()
            self.prodi_combo.addItems(self.prodi_list)
            self.prodi_combo.setEnabled(False)

            semua_mk = db_session.query(Matakuliah).all()
            self.all_matakuliah_map = defaultdict(list) 
            
            for mk in semua_mk:
                display_text = f"{mk.nama_matakuliah} ({mk.kode_mk})"
                mk_data = {"id": mk.id, "sks": mk.sks}
                key = (str(mk.semester), mk.program_studi)
                self.all_matakuliah_map[key].append((display_text, mk_data))

            self.matakuliah_map.clear()
            self.mk_combo.clear()
            self.mk_combo.setEnabled(False)

        except Exception as e:
            self.show_message("Error", f"Gagal memuat data awal: {e}")
        finally:
            db_session.close()
            
        self.clear_page()

    def clear_page(self):
        self.current_mahasiswa_id = None
        self.mhs_combo.setCurrentIndex(0)
        self.tambah_nilai_frame.setEnabled(False)
        self.table_nilai.setRowCount(0)
        self.ipk_label.setText("IPK: -")
        
        self.semester_combo.setCurrentIndex(0)
        self.semester_combo.setEnabled(False) 
        self.prodi_combo.setCurrentIndex(0)
        self.prodi_combo.setEnabled(False)
        
        self.mk_combo.clear()
        model_mk = QStandardItemModel()
        model_mk.appendRow(QStandardItem("-- Pilih Matakuliah --"))
        self.mk_combo.setModel(model_mk)
        self.mk_combo.setEnabled(False)
        
    def mahasiswa_dipilih(self):
        selected_text = self.mhs_combo.currentText()
        if selected_text == "-- Pilih Mahasiswa --":
            self.clear_page()
            return
            
        mhs_data = self.mahasiswa_map.get(selected_text)
        
        if mhs_data:
            self.current_mahasiswa_id = mhs_data["id"]
            mahasiswa_prodi = mhs_data["prodi"]
            
            self.tambah_nilai_frame.setEnabled(True) 
            self.load_transkrip(self.current_mahasiswa_id)
            
            self.prodi_combo.setCurrentText(mahasiswa_prodi)
            self.prodi_combo.setEnabled(False) 
            
            self.semester_combo.setEnabled(True)
            self.semester_combo.setCurrentIndex(0)
            
            self.mk_combo.clear()
            model_mk = QStandardItemModel()
            model_mk.appendRow(QStandardItem("-- Pilih Matakuliah --"))
            self.mk_combo.setModel(model_mk)
            self.mk_combo.setEnabled(False)
        else:
            self.clear_page() 
            
    def load_transkrip(self, mahasiswa_id):
        print(f"Memuat transkrip untuk Mahasiswa ID: {mahasiswa_id}")
        
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            hasil_query = db_session.query(
                Nilai.id, 
                Matakuliah.kode_mk, 
                Matakuliah.nama_matakuliah, 
                Matakuliah.sks,
                Nilai.nilai_huruf,
                Nilai.nilai_angka,
                Nilai.semester_diambil
            ).join(Matakuliah, Nilai.matakuliah_id == Matakuliah.id)\
             .filter(Nilai.mahasiswa_id == mahasiswa_id)\
             .all()
             
            self.table_nilai.setRowCount(0)
            
            for row_position, data in enumerate(hasil_query):
                self.table_nilai.insertRow(row_position)
                
                nomor_item = QTableWidgetItem(str(row_position + 1))
                nomor_item.setTextAlignment(Qt.AlignCenter)
                
                sks_item = QTableWidgetItem(str(data.sks))
                sks_item.setTextAlignment(Qt.AlignCenter)
                nilai_item = QTableWidgetItem(data.nilai_huruf)
                nilai_item.setTextAlignment(Qt.AlignCenter)
                bobot_item = QTableWidgetItem(str(data.nilai_angka))
                bobot_item.setTextAlignment(Qt.AlignCenter)

                self.table_nilai.setItem(row_position, 0, nomor_item) 
                self.table_nilai.setItem(row_position, 1, QTableWidgetItem(str(data.id))) 
                self.table_nilai.setItem(row_position, 2, QTableWidgetItem(data.kode_mk))
                self.table_nilai.setItem(row_position, 3, QTableWidgetItem(data.nama_matakuliah))
                self.table_nilai.setItem(row_position, 4, sks_item)
                self.table_nilai.setItem(row_position, 5, nilai_item)
                self.table_nilai.setItem(row_position, 6, bobot_item)
                semester_str = str(data.semester_diambil) if data.semester_diambil else "-"
                self.table_nilai.setItem(row_position, 7, QTableWidgetItem(semester_str))

        except Exception as e:
            self.show_message("Error", f"Gagal memuat transkrip: {e}")
        finally:
            db_session.close()
        
        self.hitung_ipk()

    def update_mk_dropdown(self):
        selected_semester = self.semester_combo.currentText()
        selected_prodi = self.prodi_combo.currentText() 
        
        self.mk_combo.clear()
        self.matakuliah_map.clear()
        
        model_mk = QStandardItemModel()
        model_mk.appendRow(QStandardItem("-- Pilih Matakuliah --"))

        if selected_semester == "-- Pilih Semester --":
            self.mk_combo.setModel(model_mk)
            self.mk_combo.setEnabled(False)
            return

        key = (selected_semester, selected_prodi)
        courses_to_load = self.all_matakuliah_map.get(key, [])
        
        for display_text, mk_data in courses_to_load:
            self.matakuliah_map[display_text] = mk_data
            item_mk = QStandardItem(display_text)
            model_mk.appendRow(item_mk)
            
        self.mk_combo.setModel(model_mk)
        self.mk_combo.setEnabled(True)

    def hitung_ipk(self):
        total_sks = 0
        total_bobot_x_sks = 0.0
        
        for row in range(self.table_nilai.rowCount()):
            try:
                sks = int(self.table_nilai.item(row, 4).text())
                bobot = float(self.table_nilai.item(row, 6).text())
                
                total_sks += sks
                total_bobot_x_sks += (sks * bobot)
            except Exception as e:
                print(f"Error hitung IPK di baris {row}: {e}") 
                
        if total_sks > 0:
            ipk = total_bobot_x_sks / total_sks
            self.current_mahasiswa_sks = total_sks
            self.current_mahasiswa_ipk = ipk
            self.ipk_label.setText(f"Total SKS: {total_sks} | IPK: {ipk:.2f}")
        else:
            self.ipk_label.setText("IPK: -")

    def simpan_nilai_baru(self):
        
        if not self.current_mahasiswa_id:
            self.show_message("Error", "Silakan pilih mahasiswa terlebih dahulu.")
            return
            
        mk_text = self.mk_combo.currentText()
        nilai_huruf = self.nilai_combo.currentText()
        
        if mk_text == "-- Pilih Matakuliah --" or self.semester_combo.currentText() == "-- Pilih Semester --":
            self.show_message("Error", "Silakan pilih semester dan matakuliah.")
            return
            
        mk_data = self.matakuliah_map.get(mk_text)
        if not mk_data:
            self.show_message("Error", "Matakuliah tidak valid.")
            return
            
        matakuliah_id = mk_data["id"]
        sks = mk_data["sks"]
        nilai_angka = self.NILAI_BOBOT_MAP[nilai_huruf]
        
        if 'SessionLocal' not in globals():
            self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
            return
            
        db_session = SessionLocal()
        try:
            nilai_ada = db_session.query(Nilai).filter_by(
                mahasiswa_id=self.current_mahasiswa_id,
                matakuliah_id=matakuliah_id
            ).first()
            
            if nilai_ada:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setWindowTitle("Konfirmasi Update")
                msg_text = f"<p style='font-size: 14px;'>Mahasiswa ini sudah memiliki nilai '{nilai_ada.nilai_huruf}' untuk matakuliah ini.<br><br>Apakah Anda ingin meng-update nilainya menjadi '{nilai_huruf}'?</p>"
                msg_box.setText(msg_text)
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                if msg_box.exec() == QMessageBox.Yes:
                    nilai_ada.nilai_huruf = nilai_huruf
                    nilai_ada.nilai_angka = nilai_angka
                    db_session.commit()
                    self.show_message("Sukses", "Nilai berhasil diperbarui.")
                else:
                    return 
            
            else:
                nilai_baru = Nilai(
                    mahasiswa_id=self.current_mahasiswa_id,
                    matakuliah_id=matakuliah_id,
                    nilai_huruf=nilai_huruf,
                    nilai_angka=nilai_angka,
                    semester_diambil=int(self.semester_combo.currentText())
                )
                db_session.add(nilai_baru)
                db_session.commit()
                self.show_message("Sukses", "Nilai baru berhasil disimpan.")

        except Exception as e:
            db_session.rollback()
            self.show_message("Error", f"Gagal menyimpan nilai: {e}")
        finally:
            db_session.close()
            
        self.load_transkrip(self.current_mahasiswa_id)

    def hapus_nilai(self):
        selected_row = self.table_nilai.currentRow()
        if selected_row < 0:
            self.show_message("Error", "Pilih nilai dari tabel yang ingin dihapus.")
            return
            
        try:
            nilai_id = int(self.table_nilai.item(selected_row, 1).text())
            mk_nama = self.table_nilai.item(selected_row, 3).text()
        except Exception as e:
            self.show_message("Error", f"Tidak bisa mendapatkan ID nilai: {e}")
            return

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_text = f"<p style='font-size: 14px;'>Apakah Anda yakin ingin menghapus nilai untuk matakuliah:<br><br><b>{mk_nama}</b>?</p>"
        msg_box.setText(msg_text)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg_box.exec() == QMessageBox.Yes:
            if 'SessionLocal' not in globals():
                self.show_message("Error", "Koneksi database (SessionLocal) tidak terdefinisi.")
                return
                
            db_session = SessionLocal()
            try:
                nilai_to_delete = db_session.query(Nilai).get(nilai_id)
                if nilai_to_delete:
                    db_session.delete(nilai_to_delete)
                    db_session.commit()
                    self.show_message("Sukses", "Nilai berhasil dihapus.")
                else:
                    self.show_message("Error", "Nilai tidak ditemukan.")
            except Exception as e:
                db_session.rollback()
                self.show_message("Error", f"Gagal menghapus nilai: {e}")
            finally:
                db_session.close()
                
            self.load_transkrip(self.current_mahasiswa_id)

    def show_message(self, title, message):
        msg_box = QMessageBox()
        if title == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_text = f"<p style='font-size: 14px;'>{message}</p>"
        msg_box.setText(msg_text)
        msg_box.exec()

# ====================================================================
# --- KARTU 2: Halaman Utama (Grafik Tren Mahasiswa Aktif) ---
# ====================================================================
class MainWidget(QWidget):
    logout_signal = Signal()

    def __init__(self, username, role): 
        super().__init__()
        self.current_username = username
        self.current_role = role
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.nav_frame = self.create_nav_frame(self.current_role) 
        main_layout.addWidget(self.nav_frame)
        
        self.page_stack = QStackedWidget()
        self.home_page = self.create_home_page() # Memanggil home page yang baru
        self.mhs_page = MahasiswaWidget()
        self.dosen_page = DosenWidget()
        self.mk_page = MatakuliahWidget() 
        self.nilai_page = NilaiWidget() 
        self.pengguna_page = PenggunaWidget(current_username=self.current_username)
        
        self.page_stack.addWidget(self.home_page)     # Indeks 0
        self.page_stack.addWidget(self.mhs_page)      # Indeks 1
        self.page_stack.addWidget(self.dosen_page)    # Indeks 2
        self.page_stack.addWidget(self.mk_page)       # Indeks 3
        self.page_stack.addWidget(self.nilai_page)    # Indeks 4
        self.page_stack.addWidget(self.pengguna_page) # Indeks 5
        
        main_layout.addWidget(self.page_stack)
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 4) 
        self.setLayout(main_layout)
        self.page_stack.setMinimumWidth(1100)
        self.chart_view.setMinimumWidth(1000)
        self.chart_view.setMinimumHeight(400)
        self.chart_view.setContentsMargins(10, 10, 30, 10)

    
    def create_nav_frame(self, user_role): 
        nav_frame = QFrame()
        nav_frame.setObjectName("nav_frame")
        nav_frame.setStyleSheet("""
            #nav_frame { background-color: #2C3E50; }
            #nav_frame QPushButton {
                font-size: 15px; font-weight: bold; color: #ECF0F1;
                background-color: transparent; border: none;
                padding: 15px; text-align: left;
            }
            #nav_frame QPushButton:hover { background-color: #34495E; }
            #nav_frame QPushButton:pressed { background-color: #283747; }
        """)
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)
        
        self.btn_home = QPushButton("Home")
        self.btn_mhs = QPushButton("Manajemen Mahasiswa")
        self.btn_dosen = QPushButton("Manajemen Dosen")
        self.btn_mk = QPushButton("Manajemen Matakuliah") 
        self.btn_nilai = QPushButton("Manajemen Nilai") 
        self.btn_pengguna = QPushButton("Manajemen Pengguna") 
        self.btn_logout = QPushButton("Logout")
        
        self.btn_home.clicked.connect(self.show_home_page)
        self.btn_mhs.clicked.connect(self.show_mhs_page) 
        self.btn_dosen.clicked.connect(self.show_dosen_page) 
        self.btn_mk.clicked.connect(self.show_mk_page) 
        self.btn_nilai.clicked.connect(self.show_nilai_page) 
        self.btn_pengguna.clicked.connect(self.show_pengguna_page) 
        self.btn_logout.clicked.connect(self.handle_logout)
        
        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_mhs)
        nav_layout.addWidget(self.btn_dosen)
        nav_layout.addWidget(self.btn_mk) 
        nav_layout.addWidget(self.btn_nilai) 
        nav_layout.addWidget(self.btn_pengguna) 
        nav_layout.addStretch() 
        nav_layout.addWidget(self.btn_logout)

        if user_role != "Admin Manajemen":
            self.btn_pengguna.hide() 

        nav_frame.setLayout(nav_layout)
        return nav_frame

    def show_home_page(self):
        """Pindah ke halaman Home dan refresh statistik"""
        try:
            self.update_dashboard_stats() # Memanggil fungsi update
        except Exception as e:
            print(f"Gagal update dashboard: {e}")
        self.page_stack.setCurrentIndex(0)

    def show_nilai_page(self):
        """Pindah ke halaman Nilai dan panggil load_data()"""
        try:
            self.nilai_page.load_initial_data() 
        except Exception as e:
            print(f"Gagal memuat data nilai: {e}")
        self.page_stack.setCurrentIndex(4) 

    def show_mk_page(self):
        try:
            self.mk_page.load_data()
            self.mk_page.search_input.clear()
            self.mk_page.filter_prodi.setCurrentIndex(0) 
            self.mk_page.filter_semester.setCurrentIndex(0) 
        except Exception as e:
            print(f"Gagal memuat data matakuliah: {e}")
        self.page_stack.setCurrentIndex(3) 

    def show_pengguna_page(self):
        try:
            self.pengguna_page.load_data()
            self.search_input.clear()
        except Exception as e:
            print(f"Gagal memuat data pengguna: {e}")
        self.page_stack.setCurrentIndex(5) 

    def show_dosen_page(self):
        try:
            self.dosen_page.load_data()
            self.dosen_page.search_input.clear()
        except Exception as e:
            print(f"Gagal memuat data dosen: {e}")
        self.page_stack.setCurrentIndex(2) 

    def show_mhs_page(self):
        try:
            self.mhs_page.load_data()
            self.mhs_page.search_input.clear() 
        except Exception as e:
            print(f"Gagal memuat data mahasiswa: {e}")
        self.page_stack.setCurrentIndex(1)

    def create_trend_chart(self):
        theme_color = QColor("#0078D7")
        self.trend_series = QLineSeries()
        self.trend_series.setName("Mahasiswa Aktif")
        self.trend_series.setPointsVisible(True)
        self.trend_series.setMarkerSize(6.0)
        self.trend_series.setColor(theme_color)

        # Seri Bayangan untuk Label Teks (agar teks naik sedikit)
        self.label_series = QScatterSeries()
        self.label_series.setMarkerSize(1.0)
        self.label_series.setColor(Qt.transparent)
        self.label_series.setPointLabelsVisible(True)
        self.label_series.setPointLabelsFormat("@yPoint")
        self.label_series.setPointLabelsColor(theme_color)
        self.label_series.setPointLabelsClipping(False)
        label_font = QFont("Arial", 10); label_font.setBold(True)
        self.label_series.setPointLabelsFont(label_font)

        chart = QChart()
        chart.addSeries(self.trend_series)
        chart.addSeries(self.label_series)
        chart.setTitle("Tren Jumlah Mahasiswa Aktif per Tahun Masuk")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setMargins(QMargins(20, 10, 20, 10))
        chart.legend().markers(self.label_series)[0].setVisible(False)

        self.trend_axis_x = QValueAxis()
        self.trend_axis_x.setTitleText("Tahun Masuk")
        self.trend_axis_x.setLabelFormat("%d")
        chart.addAxis(self.trend_axis_x, Qt.AlignBottom)
        self.trend_series.attachAxis(self.trend_axis_x)
        self.label_series.attachAxis(self.trend_axis_x)

        self.trend_axis_y = QValueAxis()
        self.trend_axis_y.setTitleText("Jumlah Mahasiswa")
        self.trend_axis_y.setLabelFormat("%d")
        chart.addAxis(self.trend_axis_y, Qt.AlignLeft)
        self.trend_series.attachAxis(self.trend_axis_y)
        self.label_series.attachAxis(self.trend_axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        return chart_view
    

    def update_dashboard_stats(self):
        if not hasattr(self, 'label_stats_mhs') or 'SessionLocal' not in globals():
            return
        
        db = SessionLocal()
        try:
            # === 1. TEKS STATISTIK ===
            count_mhs = db.query(func.count(Mahasiswa.id)).scalar() or 0
            count_dosen = db.query(func.count(Dosen.id)).scalar() or 0
            count_prodi = db.query(func.count(Mahasiswa.program_studi.distinct())).scalar() or 0
            
            self.label_stats_mhs.setText(f"Total Mahasiswa: {count_mhs}")
            self.label_stats_dosen.setText(f"Total Dosen: {count_dosen}")
            self.label_stats_prodi.setText(f"Total Program Studi: {count_prodi}")
            
            # === 2. GRAFIK TREN (LINE) ===
            self.trend_series.clear(); self.label_series.clear()
            trend_data = db.query(Mahasiswa.tahun_masuk, func.count(Mahasiswa.id))\
                           .filter(Mahasiswa.status == 'Aktif')\
                           .filter(Mahasiswa.tahun_masuk.between(2021, 2025))\
                           .group_by(Mahasiswa.tahun_masuk).order_by(Mahasiswa.tahun_masuk).all()
            
            self.trend_axis_x.setRange(2020, 2026); self.trend_axis_x.setTickCount(7)
            if trend_data:
                max_count = 0
                for tahun, jumlah in trend_data:
                    self.trend_series.append(tahun, jumlah); self.label_series.append(tahun, jumlah + 1.5)
                    if jumlah > max_count: max_count = jumlah
                self.trend_axis_y.setRange(0, max(10, max_count + 5))
            else:
                self.trend_series.append(datetime.now().year, 0); self.trend_axis_y.setRange(0, 10)

            # === 3. GRAFIK RATA-RATA IPK (BAR) ===
            self.gpa_series.clear()
            raw_gpa = db.query(Mahasiswa.program_studi, Nilai.nilai_angka, Matakuliah.sks)\
                        .join(Nilai, Mahasiswa.id == Nilai.mahasiswa_id)\
                        .join(Matakuliah, Nilai.matakuliah_id == Matakuliah.id)\
                        .filter(Mahasiswa.status == 'Aktif').all()

            stats_prodi = defaultdict(lambda: [0.0, 0])
            for prodi, val, sks in raw_gpa:
                if prodi: stats_prodi[prodi][0] += val * sks; stats_prodi[prodi][1] += sks

            bar_gpa = QBarSet("Rata-rata IPK"); bar_gpa.setColor(QColor("#27AE60")); bar_gpa.setLabelColor(Qt.white)
            label_font = QFont("Arial", 11); label_font.setBold(True); bar_gpa.setLabelFont(label_font)
            
            cats_gpa = []
            if stats_prodi:
                for prodi, d in stats_prodi.items():
                    bar_gpa.append(round(d[0]/d[1], 2) if d[1] > 0 else 0); cats_gpa.append(prodi)
            else: bar_gpa.append(0); cats_gpa.append("-")
            
            self.gpa_series.append(bar_gpa); self.gpa_axis_x.clear(); self.gpa_axis_x.append(cats_gpa)

            # === 4. GRAFIK STATUS (DONUT) ===
            self.status_series.clear()
            stat_data = db.query(Mahasiswa.status, func.count(Mahasiswa.id)).group_by(Mahasiswa.status).all()
            col_map = {"Aktif": "#28B463", "Cuti": "#F1C40F", "Lulus": "#3498DB", "DO": "#E74C3C", "Keluar": "#E74C3C"}
            tot_stat = sum([c for _, c in stat_data])
            for st, cnt in stat_data:
                pct = (cnt/tot_stat)*100 if tot_stat else 0
                sl = self.status_series.append(f"{st}: {cnt} ({pct:.1f}%)", cnt)
                if st in col_map: sl.setColor(QColor(col_map[st]))
                if st == "Aktif": sl.setExploded(True); sl.setExplodeDistanceFactor(0.1)
                sl.setLabelVisible(True)

            # === 5. GRAFIK GENDER (STACKED BAR) ===
            self.gender_series.clear()
            raw_gen = db.query(Mahasiswa.program_studi, Mahasiswa.gender, func.count(Mahasiswa.id))\
                        .filter(Mahasiswa.status == 'Aktif').group_by(Mahasiswa.program_studi, Mahasiswa.gender).all()
            gen_map = defaultdict(lambda: {'L':0, 'P':0}); cats_gen = set()
            for p, g, c in raw_gen: 
                if p: gen_map[p][g] = c; cats_gen.add(p)
            
            sorted_cats = sorted(list(cats_gen))
            set_l = QBarSet("Laki-laki"); set_l.setColor(QColor("#3498DB")); set_l.setLabelColor(Qt.white)
            set_p = QBarSet("Perempuan"); set_p.setColor(QColor("#E91E63")); set_p.setLabelColor(Qt.white)
            
            if sorted_cats:
                for p in sorted_cats: set_l.append(gen_map[p]['L']); set_p.append(gen_map[p]['P'])
            else: set_l.append(0); set_p.append(0); sorted_cats.append("-")
            
            self.gender_series.append(set_l); self.gender_series.append(set_p)
            self.gender_axis_x.clear(); self.gender_axis_x.append(sorted_cats)
            max_gen = 0
            for p in sorted_cats: 
                t = gen_map[p]['L'] + gen_map[p]['P']
                if t > max_gen: max_gen = t
            self.gender_axis_y.setRange(0, max(10, max_gen + 5))

            # === 6. GRAFIK SEBARAN IPK (BARU - HISTOGRAM STYLE) ===
            self.dist_series.clear()
            
            # Ambil data nilai per mahasiswa untuk hitung IPK individu
            raw_scores = db.query(Nilai.mahasiswa_id, Nilai.nilai_angka, Matakuliah.sks)\
                           .join(Matakuliah).filter(Mahasiswa.status == 'Aktif').all()
            
            # Hitung IPK per mahasiswa: {mhs_id: [total_poin, total_sks]}
            student_scores = defaultdict(lambda: [0, 0])
            for mid, val, sks in raw_scores:
                student_scores[mid][0] += val * sks
                student_scores[mid][1] += sks
            
            # Bucket: <2.00, 2.00-2.75, 2.76-3.50, 3.51-4.00
            buckets = [0, 0, 0, 0]
            for data in student_scores.values():
                if data[1] > 0:
                    ipk = data[0] / data[1]
                    if ipk < 2.00: buckets[0] += 1
                    elif ipk <= 2.75: buckets[1] += 1
                    elif ipk <= 3.50: buckets[2] += 1
                    else: buckets[3] += 1 # Cum Laude area
            
            bar_dist = QBarSet("Mahasiswa")
            bar_dist.setColor(QColor("#9B59B6")) # Warna Ungu (Violet)
            bar_dist.setLabelColor(Qt.white)
            
            # --- PERBAIKAN: Definisi ulang label_font di sini ---
            label_font = QFont("Arial", 11)
            label_font.setBold(True)
            bar_dist.setLabelFont(label_font)
            # ----------------------------------------------------
            
            for b in buckets:
                bar_dist.append(b)
                
            self.dist_series.append(bar_dist)
            self.dist_axis_y.setRange(0, max(10, max(buckets) + 5))

        except Exception as e:
            print(f"Gagal memuat statistik dashboard: {e}")
        finally:
            db.close()

    def create_gpa_chart(self):
        self.gpa_series = QBarSeries()
        self.gpa_series.setLabelsVisible(True) 
        self.gpa_series.setLabelsPosition(QBarSeries.LabelsCenter) # Label di tengah

        chart = QChart()
        chart.addSeries(self.gpa_series)
        chart.setTitle("Rata-rata IPK per Program Studi")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setMargins(QMargins(20, 10, 20, 10))

        self.gpa_axis_x = QBarCategoryAxis()
        self.gpa_axis_x.setTitleText("Program Studi")
        self.gpa_axis_x.setGridLineVisible(False) # Matikan grid vertikal
        chart.addAxis(self.gpa_axis_x, Qt.AlignBottom)
        self.gpa_series.attachAxis(self.gpa_axis_x)

        self.gpa_axis_y = QValueAxis()
        self.gpa_axis_y.setTitleText("Rata-rata IPK")
        self.gpa_axis_y.setRange(0, 4.0) 
        self.gpa_axis_y.setLabelFormat("%.2f") 
        chart.addAxis(self.gpa_axis_y, Qt.AlignLeft)
        self.gpa_series.attachAxis(self.gpa_axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        return chart_view

    def create_status_chart(self):
            self.status_series = QPieSeries()
            self.status_series.setHoleSize(0.40) 

            chart = QChart()
            chart.addSeries(self.status_series)
            chart.setTitle("Distribusi Status Mahasiswa")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)
            
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumHeight(400)
            return chart_view

    def create_gender_chart(self):
        self.gender_series = QStackedBarSeries()
        self.gender_series.setLabelsVisible(True)
        self.gender_series.setLabelsPosition(QBarSeries.LabelsCenter)

        chart = QChart()
        chart.addSeries(self.gender_series)
        chart.setTitle("Komposisi Gender per Program Studi")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.gender_axis_x = QBarCategoryAxis()
        self.gender_axis_x.setTitleText("Program Studi")
        self.gender_axis_x.setGridLineVisible(False)
        chart.addAxis(self.gender_axis_x, Qt.AlignBottom)
        self.gender_series.attachAxis(self.gender_axis_x)

        self.gender_axis_y = QValueAxis()
        self.gender_axis_y.setTitleText("Jumlah")
        self.gender_axis_y.setLabelFormat("%d") 
        chart.addAxis(self.gender_axis_y, Qt.AlignLeft)
        self.gender_series.attachAxis(self.gender_axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        return chart_view

    # --- FUNGSI BARU: MEMBUAT GRAFIK SEBARAN RANGE IPK ---
    def create_gpa_dist_chart(self):
        self.dist_series = QBarSeries()
        self.dist_series.setLabelsVisible(True)
        self.dist_series.setLabelsPosition(QBarSeries.LabelsCenter) # Label di tengah

        chart = QChart()
        chart.addSeries(self.dist_series)
        chart.setTitle("Sebaran Range IPK Mahasiswa")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Kategori Range IPK
        self.dist_axis_x = QBarCategoryAxis()
        self.dist_axis_x.append(["< 2.00", "2.00 - 2.75", "2.76 - 3.50", "3.51 - 4.00"])
        self.dist_axis_x.setTitleText("Range IPK")
        self.dist_axis_x.setGridLineVisible(False)
        chart.addAxis(self.dist_axis_x, Qt.AlignBottom)
        self.dist_series.attachAxis(self.dist_axis_x)

        # Sumbu Y (Jumlah Mahasiswa)
        self.dist_axis_y = QValueAxis()
        self.dist_axis_y.setTitleText("Jumlah Mahasiswa")
        self.dist_axis_y.setLabelFormat("%d") 
        chart.addAxis(self.dist_axis_y, Qt.AlignLeft)
        self.dist_series.attachAxis(self.dist_axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        
        return chart_view

    def export_dashboard_to_pdf(self):
        # 1. Pilih Lokasi Penyimpanan
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Dashboard PDF", "Laporan_Dashboard.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        # 2. Ambil Widget Konten dari Scroll Area
        # Kita mengambil widget di dalamnya, bukan scroll area-nya, agar tercetak seluruhnya (full height)
        content_widget = self.scroll_area.widget()
        
        if not content_widget:
            return

        try:
            # 3. Render Widget ke Pixmap (Gambar)
            # Menggunakan grab() untuk mengambil tampilan visual widget
            pixmap = content_widget.grab()
            
            # 4. Setup Printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize.A4) # Set ukuran kertas A4
            
            # 5. Setup Painter untuk Menggambar ke PDF
            painter = QPainter(printer)
            
            # Hitung Skala agar pas di lebar A4
            rect = printer.pageRect(QPrinter.DevicePixel).toRect()
            factor = rect.width() / pixmap.width()
            
            # Tentukan apakah perlu dipotong per halaman atau dikecilkan
            # Di sini kita akan membagi gambar jika terlalu panjang (Multi-page Logic)
            
            source_height = pixmap.height()
            current_y = 0
            
            while current_y < source_height:
                # Bagian gambar yang akan diprint di halaman ini
                page_height_in_pixmap = rect.height() / factor
                
                # Ambil potongan gambar
                source_rect = QRect(0, int(current_y), pixmap.width(), int(min(page_height_in_pixmap, source_height - current_y)))
                
                # Gambar potongan tersebut ke PDF
                target_rect = QRect(0, 0, int(source_rect.width() * factor), int(source_rect.height() * factor))
                painter.drawPixmap(target_rect, pixmap, source_rect)
                
                current_y += page_height_in_pixmap
                
                # Jika masih ada sisa gambar, buat halaman baru
                if current_y < source_height:
                    printer.newPage()
            
            painter.end()
            
            QMessageBox.information(self, "Sukses", f"Dashboard berhasil diekspor ke:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor PDF: {e}")

    def create_home_page(self):
        content_widget = QWidget()
        content_widget.setStyleSheet("QWidget { background-color: #FFFFFF; } QLabel { background-color: transparent; color: #000000; }")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # --- BAGIAN BARU: TOMBOL EXPORT DI UJUNG KIRI ---
        top_bar_layout = QHBoxLayout()
        
        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.setFixedWidth(150) # Atur lebar agar rapi
        self.btn_export_pdf.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; 
                color: white; 
                font-weight: bold;
                padding: 8px 15px; 
                border-radius: 5px; 
                border: none;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        # Hubungkan ke fungsi export (pastikan fungsi export_dashboard_to_pdf sudah ada di class)
        self.btn_export_pdf.clicked.connect(self.export_dashboard_to_pdf) 

        top_bar_layout.addWidget(self.btn_export_pdf) # Simpan di kiri
        top_bar_layout.addStretch() # Dorong sisa ruang ke kanan (agar tombol tetap di kiri)
        
        content_layout.addLayout(top_bar_layout)
        # ------------------------------------------------

        # --- Header & Stats Teks ---
        self.welcome_label = QLabel("Selamat Datang!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: 600; padding-bottom: 20px;")
        content_layout.addWidget(self.welcome_label)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        stats_layout.setAlignment(Qt.AlignCenter)
        
        stats_style = "font-size: 16px; font-weight: bold; color: #0078D7;"
        self.label_stats_mhs = QLabel("Total Mahasiswa: 0"); self.label_stats_mhs.setStyleSheet(stats_style)
        self.label_stats_dosen = QLabel("Total Dosen: 0"); self.label_stats_dosen.setStyleSheet(stats_style)
        self.label_stats_prodi = QLabel("Total Program Studi: 0"); self.label_stats_prodi.setStyleSheet(stats_style)
        
        stats_layout.addWidget(self.label_stats_mhs)
        stats_layout.addWidget(self.label_stats_dosen)
        stats_layout.addWidget(self.label_stats_prodi)
        content_layout.addLayout(stats_layout)

        # --- AREA GRAFIK ---
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(40)

        # 1. Tren Mahasiswa (Full Width)
        self.chart_view = self.create_trend_chart()
        self.chart_view.setMinimumHeight(400)
        charts_layout.addWidget(self.chart_view)
        
        # 2. Komposisi Gender (Full Width)
        self.gender_chart_view = self.create_gender_chart()
        self.gender_chart_view.setMinimumHeight(400)
        charts_layout.addWidget(self.gender_chart_view)

        # 3 & 4. Rata-rata IPK & Status (Berdampingan)
        row_34 = QHBoxLayout()
        row_34.setSpacing(20)
        
        # 3. Avg IPK (Kiri)
        self.gpa_chart_view = self.create_gpa_chart()
        self.gpa_chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        row_34.addWidget(self.gpa_chart_view)

        # 4. Status (Kanan)
        self.status_chart_view = self.create_status_chart()
        self.status_chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        row_34.addWidget(self.status_chart_view)

        charts_layout.addLayout(row_34)

        # 5. Sebaran Range IPK (Full Width)
        self.dist_chart_view = self.create_gpa_dist_chart()
        self.dist_chart_view.setMinimumHeight(400)
        charts_layout.addWidget(self.dist_chart_view)

        content_layout.addLayout(charts_layout)
        
        # --- Scroll Area ---
        from PySide6.QtWidgets import QScrollArea
        self.scroll_area = QScrollArea() 
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(content_widget)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        return self.scroll_area

    def handle_logout(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Konfirmasi Logout")
        msg_box.setText("<p style='font-size: 14px;'>Apakah Anda yakin ingin logout?</p>")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        if msg_box.exec() == QMessageBox.Yes:
            self.logout_signal.emit()

    def set_user_info(self, username, role): 
        self.current_username = username
        self.current_role = role
        
        try:
            self.welcome_label.setText(f"Selamat Datang, {self.current_username}!\n\nAnda login sebagai: {self.current_role}")
        except AttributeError:
            print("Label selamat datang belum ada.")
        
        # MEMANGGIL FUNGSI UPDATE STATS SAAT LOGIN
        self.update_dashboard_stats()

        if self.current_role != "Admin Manajemen":
            self.btn_pengguna.hide()
        else:
            self.btn_pengguna.show()

# ====================================================================
# --- WADAH UTAMA: JENDELA APLIKASI ---
# ====================================================================
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Informasi Akademik")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.login_page = LoginWidget()
        self.main_page = MainWidget(username="", role="")
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_page)
        self.login_page.login_success_signal.connect(self.show_main_page)
        self.main_page.logout_signal.connect(self.show_login_page)
        self.show_login_page()

    def show_login_page(self):
        self.stacked_widget.setCurrentIndex(0)
        self.statusBar().hide()
        self.showMaximized()
        self.login_page.input_username.clear()
        self.login_page.input_password.clear()

    def show_main_page(self, username, role): 
        self.main_page.set_user_info(username, role) 
        self.stacked_widget.setCurrentIndex(1) 
        self.statusBar().showMessage(f"Login sebagai: {username} ({role})")
        self.statusBar().show()
        self.showMaximized()

# ====================================================================
# --- Bagian 'main' ---
# ====================================================================
if __name__ == "__main__":
    if 'SessionLocal' not in globals():
        print("\n" + "="*50)
        print("ERROR: Gagal menjalankan aplikasi.")
        print("Model database (SessionLocal, Pengguna, dll.) tidak ditemukan.")
        print("Pastikan file 'database_models.py' ada di folder yang sama.")
        print("Jalankan 'python create_db.py' TERLEBIH DAHULU untuk membuat database.")
        print("="*50 + "\n")
        
        app_err = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error Kritis Aplikasi")
        msg_text = (
            "<p style='font-size: 14px;'><b>Gagal Menjalankan Aplikasi</b></p>"
            "<p style='font-size: 14px;'>Model database (SessionLocal, Pengguna, dll.) tidak ditemukan.</p>"
            "<p style='font-size: 14px;'>Pastikan file 'database_models.py' ada di folder yang sama dan "
            "Anda telah menjalankan 'python database_models.py' setidaknya satu kali.</p>"
        )
        msg_box.setText(msg_text)
        msg_box.exec()
        sys.exit(1) 
        
    app = QApplication(sys.argv)
    main_app_window = AppWindow()
    main_app_window.showMaximized()  
    sys.exit(app.exec())