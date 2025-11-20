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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

try:
    from PySide6.QtPrintSupport import QPrinter
except ImportError:
    print("Modul QtPrintSupport tidak ditemukan. Pastikan instalasi PySide6 lengkap.")

from database_models import SessionLocal, Pengguna, Mahasiswa, Dosen, Matakuliah, Nilai, AuditLog

def log_activity(username, action, table, details):
    """
    Mencatat aktivitas ke tabel audit_logs
    """
    if 'SessionLocal' not in globals(): return
    
    db = SessionLocal()
    try:
        log = AuditLog(
            username=username,
            action=action,
            table_name=table,
            details=details
        )
        db.add(log)
        db.commit()
        print(f"[AUDIT] {username} - {action} - {details}")
    except Exception as e:
        print(f"Gagal mencatat log: {e}")
        db.rollback()
    finally:
        db.close()

class ClickableCard(QFrame):
    clicked = Signal() # Sinyal kustom saat diklik

    def mousePressEvent(self, event):
        self.clicked.emit() # Pancarkan sinyal
        super().mousePressEvent(event)
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
        self.title_label = QLabel("SISTEM AKADEMIK")
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
        # Setup background utama aplikasi (misal: gradasi abu-abu ke biru muda)
        self.setStyleSheet("""
            LoginWidget { 
                background-color: #E8F0FE; 
            }
            
            /* --- KOTAK LOGIN (CARD) --- */
            #login_frame {
                background-color: #FFFFFF; 
                border-radius: 20px;
                border: 1px solid #D1D9E6;
                /* Simulasi Shadow halus lewat border tebal di sisi tertentu */
                border-bottom: 4px solid #D1D9E6;
                border-right: 2px solid #D1D9E6;
            }

            /* --- JUDUL --- */
            #title_label {
                font-family: 'Segoe UI', sans-serif;
                font-size: 26px;
                font-weight: 800;
                color: #2C3E50;
                margin-bottom: 10px;
            }

            /* --- LABEL (Username/Password) --- */
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                color: #555555;
                font-weight: 600;
                margin-bottom: 2px;
            }

            /* --- INPUT FIELDS --- */
            QLineEdit {
                font-size: 14px;
                background-color: #F8F9FA; 
                border: 2px solid #E9ECEF; 
                border-radius: 10px;
                padding: 12px 15px; /* Padding diperbesar agar lega */
                color: #333333; 
            }
            
            /* Efek saat diklik/fokus */
            QLineEdit:focus { 
                border: 2px solid #0078D7; 
                background-color: #FFFFFF;
            }

            /* --- TOMBOL LOGIN --- */
            #login_button {
                font-family: 'Segoe UI', sans-serif;
                font-size: 16px; 
                font-weight: bold;
                background-color: #0078D7; 
                color: white;
                border: none; 
                border-radius: 10px; 
                padding: 15px;
                margin-top: 10px;
            }
            
            /* Efek Hover (saat mouse di atas tombol) */
            #login_button:hover { 
                background-color: #005A9E; 
            }
            
            /* Efek Pressed (saat tombol ditekan) */
            #login_button:pressed { 
                background-color: #004A8C; 
                padding-top: 17px; /* Efek tombol tertekan ke dalam */
                padding-bottom: 13px;
            }
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
    
    def __init__(self, current_username):
        super().__init__()
        self.current_username = current_username
        self.selected_mahasiswa_id = None
        
        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.form_frame = QFrame() 
        self.form_frame.setObjectName("form_frame")
        self.form_frame.setFixedWidth(320) 
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
        
        self.input_dosen_wali.addItem("Pilih Dosen Wali", None)
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
        main_layout.setStretch(0, 0) 
        main_layout.setStretch(1, 2) 

        self.btn_update.clicked.connect(self.update_data) 
        self.btn_import.clicked.connect(self.import_from_excel) 
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_bersihkan.clicked.connect(self.clear_form)
        self.btn_hapus.clicked.connect(self.delete_data)
        self.table_mhs.itemClicked.connect(self.table_row_clicked)
        self.search_input.textChanged.connect(self.filter_table)
        self.load_dosen_options()
        self.applyStyles()
        self.load_data()

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
        self.input_dosen_wali.addItem("Pilih Dosen Wali", None)
        
        if 'SessionLocal' not in globals(): return
        
        db = SessionLocal()
        try:
            dosen_list = db.query(Dosen).all()
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
                log_activity(
                    self.current_username, 
                    "UPDATE", 
                    "Mahasiswa", 
                    f"Memperbarui data mahasiswa NIM: {nim}, Nama: {nama}"
                )
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
                    log_activity(
                        self.current_username, 
                        "DELETE", 
                        "Mahasiswa", 
                        f"Menghapus mahasiswa ID: {self.selected_mahasiswa_id}"
                    )
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

    def __init__(self, current_username):
        super().__init__()
        self.current_username = current_username
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
        form_layout.addRow(QLabel("NIDN/NIP:"), self.input_nidn)
        form_layout.addRow(QLabel("Nama Lengkap:"), self.input_nama)
        form_layout.addRow(QLabel("Gender (L/P):"), self.input_gender)
        form_layout.addRow(QLabel("Jabatan Akademik:"), self.input_jabatan)
        form_layout.addRow(QLabel("Email:"), self.input_email)
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
        self.table_dsn.setColumnCount(7) 
        self.table_dsn.setHorizontalHeaderLabels([
            "#", "ID", "NIDN", "Nama", 
            "Gender", "Jabatan Akademik", "Email" 
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
            "Jabatan Akademik", "Email"
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
        self.selected_dosen_id = dsn_id
        self.input_nidn.setText(nidn)
        self.input_nama.setText(nama)
        self.input_gender.setCurrentText(gender)
        self.input_jabatan.setCurrentText(jabatan)
        self.input_email.setText(email)

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
        self.load_data()    

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
                    log_activity(self.current_username, "UPDATE", "Pengguna", f"Update User: {username} Role: {role}")
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
                log_activity(self.current_username, "CREATE", "Pengguna", f"Buat User Baru: {username} Role: {role}")
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
            db_session = SessionLocal()
            try:
                user = db_session.query(Pengguna).get(self.selected_pengguna_id)
                if user:
                    nama_hapus = user.username
                    db_session.delete(user)
                    log_activity(self.current_username, "DELETE", "Pengguna", f"Hapus User: {nama_hapus}")
                    db_session.commit()
                    self.show_message("Sukses", f"Pengguna '{nama_hapus}' berhasil dihapus.")
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

    def __init__(self, current_username):
        super().__init__()
        self.current_username = current_username
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
        self.load_data() 

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
                log_activity(self.current_username, "UPDATE", "Matakuliah", f"Update MK: {kode} - {nama}")
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

    def __init__(self, current_username):
        super().__init__()
        self.current_username = current_username
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
        
        # --- BAGIAN PEMILIHAN MAHASISWA ---
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

        # --- BAGIAN INPUT NILAI ---
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

        # --- BAGIAN TABEL TRANSKRIP ---
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
        
        # --- BUTTONS ACTION (HAPUS & CETAK) ---
        action_btn_layout = QHBoxLayout()
        
        self.btn_hapus_nilai = QPushButton("Hapus Nilai Terpilih")
        self.btn_hapus_nilai.setObjectName("btn_hapus")
        
        # -- TOMBOL BARU: CETAK TRANSKRIP --
        self.btn_cetak_transkrip = QPushButton("Cetak Transkrip Lengkap (PDF)")
        self.btn_cetak_transkrip.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; 
                color: white; 
                font-weight: bold; 
                padding: 10px; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #219150; }
        """)
        
        action_btn_layout.addWidget(self.btn_hapus_nilai)
        action_btn_layout.addStretch() # Pemisah
        action_btn_layout.addWidget(self.btn_cetak_transkrip)
        
        transkrip_layout.addLayout(action_btn_layout)
        
        main_layout.addWidget(transkrip_frame)
        
        # --- KONEKSI SINYAL ---
        self.mhs_combo.activated.connect(self.mahasiswa_dipilih)
        self.semester_combo.activated.connect(self.update_mk_dropdown)
        self.btn_simpan_nilai.clicked.connect(self.simpan_nilai_baru)
        self.btn_hapus_nilai.clicked.connect(self.hapus_nilai)
        self.btn_cetak_transkrip.clicked.connect(self.print_transkrip) # Koneksi fungsi baru
        
        self.applyStyles()
        self.load_initial_data()

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
        if 'SessionLocal' not in globals(): return
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
        self.btn_cetak_transkrip.setEnabled(False) # Disable tombol cetak jika belum pilih mhs

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
            self.semester_combo.setEnabled(True)
            self.semester_combo.setCurrentIndex(0)
            self.mk_combo.clear()
            model_mk = QStandardItemModel()
            model_mk.appendRow(QStandardItem("-- Pilih Matakuliah --"))
            self.mk_combo.setModel(model_mk)
            self.mk_combo.setEnabled(False)
            self.btn_cetak_transkrip.setEnabled(True) # Enable tombol cetak
        else:
            self.clear_page() 

    def load_transkrip(self, mahasiswa_id):
        if 'SessionLocal' not in globals(): return
        db_session = SessionLocal()
        try:
            hasil_query = db_session.query(
                Nilai.id, Matakuliah.kode_mk, Matakuliah.nama_matakuliah, 
                Matakuliah.sks, Nilai.nilai_huruf, Nilai.nilai_angka, Nilai.semester_diambil
            ).join(Matakuliah, Nilai.matakuliah_id == Matakuliah.id)\
             .filter(Nilai.mahasiswa_id == mahasiswa_id).all()
             
            self.table_nilai.setRowCount(0)
            for row_position, data in enumerate(hasil_query):
                self.table_nilai.insertRow(row_position)
                # ... (kode insert item sama seperti sebelumnya)
                self.table_nilai.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1))) 
                self.table_nilai.setItem(row_position, 1, QTableWidgetItem(str(data.id))) 
                self.table_nilai.setItem(row_position, 2, QTableWidgetItem(data.kode_mk))
                self.table_nilai.setItem(row_position, 3, QTableWidgetItem(data.nama_matakuliah))
                
                item_sks = QTableWidgetItem(str(data.sks)); item_sks.setTextAlignment(Qt.AlignCenter)
                self.table_nilai.setItem(row_position, 4, item_sks)
                
                item_huruf = QTableWidgetItem(data.nilai_huruf); item_huruf.setTextAlignment(Qt.AlignCenter)
                self.table_nilai.setItem(row_position, 5, item_huruf)
                
                item_angka = QTableWidgetItem(str(data.nilai_angka)); item_angka.setTextAlignment(Qt.AlignCenter)
                self.table_nilai.setItem(row_position, 6, item_angka)
                
                self.table_nilai.setItem(row_position, 7, QTableWidgetItem(str(data.semester_diambil or "-")))
        except Exception as e:
            self.show_message("Error", f"Gagal memuat transkrip: {e}")
        finally:
            db_session.close()
        self.hitung_ipk()

    def update_mk_dropdown(self):
        # ... (Kode sama seperti sebelumnya)
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
            except: pass
        if total_sks > 0:
            ipk = total_bobot_x_sks / total_sks
            self.current_mahasiswa_sks = total_sks
            self.current_mahasiswa_ipk = ipk
            self.ipk_label.setText(f"Total SKS: {total_sks} | IPK: {ipk:.2f}")
        else:
            self.current_mahasiswa_sks = 0
            self.current_mahasiswa_ipk = 0.0
            self.ipk_label.setText("IPK: -")

    def simpan_nilai_baru(self):
        # ... (Kode sama seperti sebelumnya)
        if not self.current_mahasiswa_id: return
        mk_text = self.mk_combo.currentText()
        nilai_huruf = self.nilai_combo.currentText()
        if mk_text == "-- Pilih Matakuliah --" or self.semester_combo.currentText() == "-- Pilih Semester --":
            self.show_message("Error", "Pilih semester dan matakuliah.")
            return
        mk_data = self.matakuliah_map.get(mk_text)
        matakuliah_id = mk_data["id"]
        nilai_angka = self.NILAI_BOBOT_MAP[nilai_huruf]
        if 'SessionLocal' not in globals(): return
        db_session = SessionLocal()
        try:
            nilai_ada = db_session.query(Nilai).filter_by(mahasiswa_id=self.current_mahasiswa_id, matakuliah_id=matakuliah_id).first()
            if nilai_ada:
                if QMessageBox.question(self, "Konfirmasi", "Update nilai?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                    nilai_ada.nilai_huruf = nilai_huruf
                    nilai_ada.nilai_angka = nilai_angka
                    log_activity(self.current_username, "UPDATE", "Nilai", f"Update Nilai Mhs ID {self.current_mahasiswa_id}: MK {mk_text} -> {nilai_huruf}")
                    db_session.commit()
                    self.show_message("Sukses", "Nilai diperbarui.")
            else:
                db_session.add(Nilai(mahasiswa_id=self.current_mahasiswa_id, matakuliah_id=matakuliah_id, nilai_huruf=nilai_huruf, nilai_angka=nilai_angka, semester_diambil=int(self.semester_combo.currentText())))
                log_activity(self.current_username, "CREATE", "Nilai", f"Input Nilai Mhs ID {self.current_mahasiswa_id}: MK {mk_text} -> {nilai_huruf}")
                db_session.commit()
                self.show_message("Sukses", "Nilai disimpan.")
        except Exception as e: db_session.rollback(); self.show_message("Error", str(e))
        finally: db_session.close()
        self.load_transkrip(self.current_mahasiswa_id)

    def hapus_nilai(self):
        row = self.table_nilai.currentRow()
        if row < 0: return self.show_message("Error", "Pilih nilai.")
        nilai_id = int(self.table_nilai.item(row, 1).text())
        if QMessageBox.question(self, "Hapus", "Yakin hapus nilai?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                val = db.query(Nilai).get(nilai_id)
                if val:
                    log_activity(self.current_username, "DELETE", "Nilai", f"Hapus Nilai ID {nilai_id}")
                    db.delete(val)
                    db.commit()
                    self.show_message("Sukses", "Nilai dihapus.")
            except Exception as e: db.rollback(); self.show_message("Error", str(e))
            finally: db.close()
            self.load_transkrip(self.current_mahasiswa_id)

    def print_transkrip(self):
        if not self.current_mahasiswa_id:
            self.show_message("Error", "Pilih mahasiswa terlebih dahulu.")
            return

        # 1. Ambil Data Lengkap dari Database
        db = SessionLocal()
        try:
            mhs = db.query(Mahasiswa).get(self.current_mahasiswa_id)
            doswal_nama = mhs.dosen_wali.nama if mhs.dosen_wali else "Belum ditentukan"
            doswal_nidn = mhs.dosen_wali.nidn if mhs.dosen_wali else "-"
            
            # Ambil semua nilai untuk tabel transkrip
            nilai_list = db.query(Nilai, Matakuliah)\
                           .join(Matakuliah, Nilai.matakuliah_id == Matakuliah.id)\
                           .filter(Nilai.mahasiswa_id == mhs.id)\
                           .order_by(Nilai.semester_diambil, Matakuliah.kode_mk).all()
        except Exception as e:
            self.show_message("Error", f"Gagal mengambil data database: {e}")
            db.close()
            return
        finally:
            db.close()

        # 2. Pilih Lokasi Simpan
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan Transkrip", f"Transkrip_{mhs.nim}.pdf", "PDF Files (*.pdf)"
        )
        if not filename: return

        # 3. Buat Dokumen PDF ReportLab
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()
        
        # --- JUDUL ---
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=20)
        elements.append(Paragraph("TRANSKRIP AKADEMIK MAHASISWA", title_style))
        elements.append(Spacer(1, 10))

        # --- DATA DIRI (Header Tabel Transparan) ---
        # Format: [Label, Value, Label, Value]
        info_data = [
            [Paragraph("<b>Nama Lengkap</b>", styles["Normal"]), ": " + mhs.nama, Paragraph("<b>Program Studi</b>", styles["Normal"]), ": " + mhs.program_studi],
            [Paragraph("<b>NIM</b>", styles["Normal"]), ": " + mhs.nim, Paragraph("<b>Tahun Masuk</b>", styles["Normal"]), ": " + str(mhs.tahun_masuk)],
            [Paragraph("<b>Tempat/Tgl Lahir</b>", styles["Normal"]), ": " + (mhs.tanggal_lahir.strftime("%d-%m-%Y") if mhs.tanggal_lahir else "-"), Paragraph("<b>Dosen Wali</b>", styles["Normal"]), ": " + doswal_nama],
        ]
        
        info_table = Table(info_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 2.5*inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # --- TABEL NILAI ---
        # Header Tabel
        table_data = [['No', 'Smt', 'Kode MK', 'Matakuliah', 'SKS', 'Nilai', 'Bobot']]
        
        total_sks = 0
        total_poin = 0
        
        for i, (n, mk) in enumerate(nilai_list, 1):
            bobot_total = n.nilai_angka * mk.sks
            total_sks += mk.sks
            total_poin += bobot_total
            
            row = [
                str(i),
                str(n.semester_diambil),
                mk.kode_mk,
                Paragraph(mk.nama_matakuliah, styles["BodyText"]), # Pakai Paragraph agar wrap text kalau panjang
                str(mk.sks),
                n.nilai_huruf,
                f"{n.nilai_angka:.2f}"
            ]
            table_data.append(row)

        # Hitung IPK Akhir
        ipk_akhir = total_poin / total_sks if total_sks > 0 else 0.00

        # Buat Tabel ReportLab
        # Tentukan lebar kolom agar pas A4
        col_widths = [0.4*inch, 0.5*inch, 1.0*inch, 2.8*inch, 0.5*inch, 0.6*inch, 0.6*inch]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Styling Tabel Nilai (Grid, Header Bold, Zebra striping optional)
        tbl_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")), # Header Gelap
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),           # Teks Header Putih
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),                       # Default Center
            ('ALIGN', (3,1), (3,-1), 'LEFT'),                          # Nama MK Left Align
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),               # Garis Kotak
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
        t.setStyle(tbl_style)
        elements.append(t)
        elements.append(Spacer(1, 20))

        # --- FOOTER (Ringkasan & Tanda Tangan) ---
        summary_data = [
            ["Total SKS Diambil", f"   : {total_sks}"],
            ["Indeks Prestasi Kumulatif (IPK)", f"   : {ipk_akhir:.2f}"],
            ["Predikat Kelulusan", f"   : {'Cum Laude' if ipk_akhir > 3.5 else 'Sangat Memuaskan' if ipk_akhir > 3.0 else 'Memuaskan'}"]
        ]
        
        # Tabel Ringkasan di Kiri
        sum_table = Table(summary_data, colWidths=[2*inch, 1*inch], hAlign='LEFT')
        sum_table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold')]))
        
        # Area Tanda Tangan di Kanan
        current_date = datetime.now().strftime("%d %B %Y")
        ttd_content = [
            [Paragraph(f"Manado, {current_date}", styles["Normal"])],
            [Paragraph("Mengetahui, Kaprodi", styles["Normal"])],
            [""], [" "], [" "], # Spasi Tanda Tangan
            [Paragraph(f"<u>( ........................... )</u>", styles["Normal"])]
        ]
        ttd_table = Table(ttd_content, colWidths=[2.5*inch])
        ttd_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))

        # Gabungkan Summary (Kiri) dan TTD (Kanan) dalam satu tabel layout invisible
        footer_layout = Table([[sum_table, ttd_table]], colWidths=[3.5*inch, 3*inch])
        elements.append(footer_layout)

        # 4. Build PDF
        try:
            doc.build(elements)
            log_activity(self.current_username, "EXPORT", "Transkrip", f"Export PDF Transkrip {mhs.nim}")
            self.show_message("Sukses", f"Transkrip berhasil disimpan di:\n{filename}")
        except Exception as e:
            self.show_message("Error", f"Gagal membuat PDF: {e}")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information if title == "Sukses" else QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
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
        self.home_page = self.create_home_page() 
        self.mhs_page = MahasiswaWidget(self.current_username)
        self.dosen_page = DosenWidget(self.current_username)
        self.mk_page = MatakuliahWidget(self.current_username) 
        self.nilai_page = NilaiWidget(self.current_username) 
        self.pengguna_page = PenggunaWidget(current_username=self.current_username)
        self.audit_page = AuditLogWidget()
        
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
        self.audit_page = AuditLogWidget()                      
        self.page_stack.addWidget(self.audit_page) 

    
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
        self.btn_audit = QPushButton("Audit Log")
        self.btn_audit.clicked.connect(self.show_audit_page)
        
        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_mhs)
        nav_layout.addWidget(self.btn_dosen)
        nav_layout.addWidget(self.btn_mk) 
        nav_layout.addWidget(self.btn_nilai) 
        nav_layout.addWidget(self.btn_pengguna) 
        nav_layout.addStretch() 
        nav_layout.addWidget(self.btn_audit)
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
        self.trend_series.setMarkerSize(4.0) # Ukuran titik sedikit diperbesar
        self.trend_series.setColor(theme_color)

        # Seri Bayangan untuk Label Teks
        self.label_series = QScatterSeries()
        self.label_series.setMarkerSize(1.0)
        self.label_series.setColor(Qt.transparent)
        self.label_series.setPointLabelsVisible(True)
        
        format_label = "@yPoint" + ("\n" * 10) + " "
        self.label_series.setPointLabelsFormat(format_label)
        # --------------------------

        self.label_series.setPointLabelsColor(theme_color)
        
        # PENTING: Matikan clipping agar teks tidak terpotong jika melewati garis atas grafik
        self.label_series.setPointLabelsClipping(False) 
        
        label_font = QFont("Arial", 11); label_font.setBold(True)
        self.label_series.setPointLabelsFont(label_font)

        chart = QChart()
        chart.addSeries(self.trend_series)
        chart.addSeries(self.label_series)
        chart.setTitle("Tren Jumlah Mahasiswa Aktif per Tahun Masuk")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setMargins(QMargins(20, 10, 20, 10))
        
        # Sembunyikan marker label dari legenda
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
    
    def show_audit_page(self):
        self.audit_page.load_data() # Refresh data saat dibuka
        self.page_stack.setCurrentWidget(self.audit_page)
    
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
            self.trend_series.clear()
            self.label_series.clear()
            
            trend_data = db.query(Mahasiswa.tahun_masuk, func.count(Mahasiswa.id))\
                           .filter(Mahasiswa.status == 'Aktif')\
                           .filter(Mahasiswa.tahun_masuk.between(2021, 2025))\
                           .group_by(Mahasiswa.tahun_masuk)\
                           .order_by(Mahasiswa.tahun_masuk).all()
            
            self.trend_axis_x.setRange(2020, 2026)
            self.trend_axis_x.setTickCount(7)

            if trend_data:
                max_count = 0
                for tahun, jumlah in trend_data:
                    self.trend_series.append(tahun, jumlah)
                    
                    # --- PERUBAHAN DI SINI ---
                    # Hapus "+ 1.5". Gunakan 'jumlah' murni agar format label (@yPoint) menjadi integer.
                    # Posisi text akan turun tepat ke titik data, namun angka akan sesuai (bulat).
                    self.label_series.append(tahun, jumlah) 
                    
                    if jumlah > max_count: max_count = jumlah
                
                # Tambahkan padding atas agar label tidak terpotong
                self.trend_axis_y.setRange(0, max(10, max_count + 5))
            else:
                current_year = datetime.now().year
                self.trend_series.append(current_year - 1, 0)
                self.trend_series.append(current_year, 0)
                self.trend_axis_y.setRange(0, 10)

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

            # === 6. GRAFIK SEBARAN IPK ===
            self.dist_series.clear()
            raw_scores = db.query(Nilai.mahasiswa_id, Nilai.nilai_angka, Matakuliah.sks)\
                           .join(Matakuliah).filter(Mahasiswa.status == 'Aktif').all()
            
            student_scores = defaultdict(lambda: [0, 0])
            for mid, val, sks in raw_scores:
                student_scores[mid][0] += val * sks
                student_scores[mid][1] += sks
            
            buckets = [0, 0, 0, 0]
            for data in student_scores.values():
                if data[1] > 0:
                    ipk = data[0] / data[1]
                    if ipk < 2.00: buckets[0] += 1
                    elif ipk <= 2.75: buckets[1] += 1
                    elif ipk <= 3.50: buckets[2] += 1
                    else: buckets[3] += 1 
            
            bar_dist = QBarSet("Mahasiswa")
            bar_dist.setColor(QColor("#9B59B6")) 
            bar_dist.setLabelColor(Qt.white)
            label_font = QFont("Arial", 11)
            label_font.setBold(True)
            bar_dist.setLabelFont(label_font)
            
            for b in buckets:
                bar_dist.append(b)
                
            self.dist_series.append(bar_dist)
            self.dist_axis_y.setRange(0, max(10, max(buckets) + 5))
            
            # === A. DATA JABATAN DOSEN (Refresh Data) ===
            self.jabatan_series.clear()
            jabatan_data = db.query(Dosen.jabatan_akademik, func.count(Dosen.id)).group_by(Dosen.jabatan_akademik).all()
            colors_jabatan = ["#3498DB", "#E67E22", "#9B59B6", "#2ECC71", "#F1C40F"]
            
            total_dosen_jab = sum([c for _, c in jabatan_data])
            for i, (jab, cnt) in enumerate(jabatan_data):
                if not jab: jab = "Tanpa Jabatan"
                pct = (cnt/total_dosen_jab)*100 if total_dosen_jab else 0
                sl = self.jabatan_series.append(f"{jab}: {cnt}", cnt)
                sl.setLabelVisible(True)
                sl.setColor(QColor(colors_jabatan[i % len(colors_jabatan)]))

            # === B. DATA GENDER DOSEN ===
            self.dosen_gender_series.clear()
            dosen_gen_data = db.query(Dosen.gender, func.count(Dosen.id)).group_by(Dosen.gender).all()
            color_map_gen = {'L': "#2980B9", 'P': "#E91E63"} # Biru & Pink
            
            total_dosen_gen = sum([c for _, c in dosen_gen_data])
            for gen, cnt in dosen_gen_data:
                label_gen = "Laki-laki" if gen == 'L' else "Perempuan"
                pct = (cnt/total_dosen_gen)*100 if total_dosen_gen else 0
                sl = self.dosen_gender_series.append(f"{label_gen} ({pct:.1f}%)", cnt)
                sl.setLabelVisible(True)
                if gen in color_map_gen: sl.setColor(QColor(color_map_gen[gen]))

            # === C. DATA TOP DOSEN WALI ===
            self.doswal_series.clear()
            self.axis_x_doswal.clear()
            
            # Query: Join Dosen & Mahasiswa, Group by Dosen, Count Mahasiswa
            top_doswal = db.query(Dosen.nama, func.count(Mahasiswa.id))\
                           .join(Mahasiswa, Dosen.id == Mahasiswa.dosen_wali_id)\
                           .filter(Mahasiswa.status == 'Aktif')\
                           .group_by(Dosen.id)\
                           .order_by(func.count(Mahasiswa.id).desc())\
                           .limit(5).all()
            
            bar_set_doswal = QBarSet("Mahasiswa")
            bar_set_doswal.setColor(QColor("#16A085")) # Warna Teal
            
            cats_doswal = []
            max_val_doswal = 0
            
            if top_doswal:
                for nama, jumlah in top_doswal:
                    # Persingkat nama jika terlalu panjang untuk grafik
                    nama_display = nama.split(',')[0] if ',' in nama else nama 
                    if len(nama_display) > 15: nama_display = nama_display[:12] + "..."
                    
                    bar_set_doswal.append(jumlah)
                    cats_doswal.append(nama_display)
                    if jumlah > max_val_doswal: max_val_doswal = jumlah
            else:
                bar_set_doswal.append(0)
                cats_doswal.append("-")

            self.doswal_series.append(bar_set_doswal)
            self.axis_x_doswal.append(cats_doswal)
            self.axis_y_doswal.setRange(0, max(5, max_val_doswal + 2))

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
    
    # --- GRAFIK BARU: GENDER DOSEN ---
    def create_dosen_gender_chart(self):
        self.dosen_gender_series = QPieSeries()
        self.dosen_gender_series.setHoleSize(0.40) # Donut style

        chart = QChart()
        chart.addSeries(self.dosen_gender_series)
        chart.setTitle("Rasio Gender Dosen")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        return chart_view

    # --- GRAFIK BARU: BEBAN DOSEN WALI (TOP 5) ---
    def create_top_doswal_chart(self):
        self.doswal_series = QBarSeries()
        self.doswal_series.setLabelsVisible(True)
        self.doswal_series.setLabelsPosition(QBarSeries.LabelsCenter)

        chart = QChart()
        chart.addSeries(self.doswal_series)
        chart.setTitle("Top 5 Dosen dengan Mahasiswa Wali Terbanyak")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        self.axis_x_doswal = QBarCategoryAxis()
        self.axis_x_doswal.setTitleText("Nama Dosen")
        chart.addAxis(self.axis_x_doswal, Qt.AlignBottom)
        self.doswal_series.attachAxis(self.axis_x_doswal)

        self.axis_y_doswal = QValueAxis()
        self.axis_y_doswal.setTitleText("Jumlah Mahasiswa")
        self.axis_y_doswal.setLabelFormat("%d")
        chart.addAxis(self.axis_y_doswal, Qt.AlignLeft)
        self.doswal_series.attachAxis(self.axis_y_doswal)

        chart.legend().setVisible(False) # Tidak perlu legenda untuk bar simple

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
        content_widget.setStyleSheet("QWidget { background-color: #FFFFFF; }")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setContentsMargins(40, 40, 40, 40)

        # --- 1. HEADER ---
        header_layout = QHBoxLayout()
        
        self.welcome_label = QLabel(f"Selamat Datang, {self.current_username}!")
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #000000;")
        
        self.btn_reset_filter = QPushButton("Tampilkan Semua")
        self.btn_reset_filter.setCursor(Qt.PointingHandCursor)
        self.btn_reset_filter.hide()
        self.btn_reset_filter.setStyleSheet("""
            QPushButton { background-color: #34495E; color: white; border-radius: 5px; padding: 8px 15px; font-weight: bold;}
            QPushButton:hover { background-color: #2C3E50; }
        """)
        self.btn_reset_filter.clicked.connect(lambda: self.filter_dashboard("ALL"))

        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_reset_filter)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(20)

        # --- 2. AREA KARTU STATISTIK ---
        stats_container = QHBoxLayout()
        stats_container.setSpacing(20)
        stats_container.setContentsMargins(0, 0, 0, 20)

        def create_card(icon_emoji, object_name, label_text):
            card = ClickableCard() 
            card.setCursor(Qt.PointingHandCursor)
            card.setStyleSheet("""
                ClickableCard {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 15px;
                }
                ClickableCard:hover {
                    border: 2px solid #70AD47;
                    background-color: #F9FFF9;
                }
            """)
            card.setFixedSize(250, 120)

            layout = QVBoxLayout(card)
            layout.setAlignment(Qt.AlignCenter)
            layout.setSpacing(5)

            lbl_icon = QLabel(icon_emoji)
            lbl_icon.setAlignment(Qt.AlignCenter)
            lbl_icon.setStyleSheet("font-size: 40px; color: #70AD47; border: none; background: transparent;")
            
            lbl_value = QLabel("Loading...")
            lbl_value.setObjectName(object_name)
            lbl_value.setAlignment(Qt.AlignCenter)
            lbl_value.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333; border: none; background: transparent;")
            
            lbl_title = QLabel(label_text)
            lbl_title.setAlignment(Qt.AlignCenter)
            lbl_title.setStyleSheet("font-size: 12px; color: #777; border: none; background: transparent;")

            layout.addWidget(lbl_icon)
            layout.addWidget(lbl_value)
            layout.addWidget(lbl_title)
            
            return card, lbl_value

        self.card_mhs, self.label_stats_mhs = create_card("🎓", "stats_mhs", "Mahasiswa")
        self.card_mhs.clicked.connect(lambda: self.filter_dashboard("MAHASISWA"))
        stats_container.addWidget(self.card_mhs)

        self.card_dosen, self.label_stats_dosen = create_card("💼", "stats_dosen", "Dosen")
        self.card_dosen.clicked.connect(lambda: self.filter_dashboard("DOSEN"))
        stats_container.addWidget(self.card_dosen)

        self.card_prodi, self.label_stats_prodi = create_card("🏛️", "stats_prodi", "Program Studi")
        self.card_prodi.clicked.connect(lambda: self.filter_dashboard("PRODI"))
        stats_container.addWidget(self.card_prodi)

        stats_container.addStretch()

        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.setFixedSize(150, 50)
        self.btn_export_pdf.setStyleSheet("""
            QPushButton { background-color: #70AD47; color: white; font-weight: bold; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #5D9138; }
        """)
        self.btn_export_pdf.clicked.connect(self.export_dashboard_to_pdf)
        stats_container.addWidget(self.btn_export_pdf)

        content_layout.addLayout(stats_container)

        # --- 3. AREA GRAFIK (MODIFIKASI AGAR VERTIKAL) ---
        self.charts_layout = QVBoxLayout()
        self.charts_layout.setSpacing(40) # Jarak antar grafik vertikal

        # --- INITIALIZE CHART VIEWS ---
        # [A] Grafik Mahasiswa
        self.chart_view = self.create_trend_chart()
        self.gender_chart_view = self.create_gender_chart()
        self.status_chart_view = self.create_status_chart()
        self.dist_chart_view = self.create_gpa_dist_chart()

        # [B] Grafik Dosen
        if hasattr(self, 'create_jabatan_dosen_chart'):
            self.jabatan_chart_view = self.create_jabatan_dosen_chart()
        else:
            self.jabatan_chart_view = QWidget()
            
        if hasattr(self, 'create_dosen_gender_chart'):
            self.dosen_gender_view = self.create_dosen_gender_chart()
        else:
            self.dosen_gender_view = QWidget()

        if hasattr(self, 'create_top_doswal_chart'):
            self.doswal_chart_view = self.create_top_doswal_chart()
        else:
            self.doswal_chart_view = QWidget()

        # [C] Grafik Prodi
        self.gpa_chart_view = self.create_gpa_chart()

        # --- MENYUSUN LAYOUT SECARA BERURUTAN KE BAWAH (VERTIKAL) ---
        # Kita menambahkan semuanya langsung ke `charts_layout` (QVBoxLayout)
        # Tanpa menggunakan QHBoxLayout (Horizontal) pembungkus.

        # 1. Kelompok Mahasiswa
        self.charts_layout.addWidget(self.chart_view)       # Tren
        self.charts_layout.addWidget(self.gender_chart_view)# Gender Mhs
        self.charts_layout.addWidget(self.status_chart_view)# Status Mhs
        self.charts_layout.addWidget(self.dist_chart_view)  # Sebaran IPK

        # 2. Kelompok Dosen (SEKARANG VERTIKAL)
        self.charts_layout.addWidget(self.jabatan_chart_view) # Pie Chart Jabatan
        self.charts_layout.addWidget(self.dosen_gender_view)  # Donut Chart Gender Dosen
        self.charts_layout.addWidget(self.doswal_chart_view)  # Bar Chart Top Doswal

        # 3. Kelompok Prodi
        self.charts_layout.addWidget(self.gpa_chart_view)     # Bar Chart IPK Prodi

        content_layout.addLayout(self.charts_layout)
        
        # Scroll Area Setup
        from PySide6.QtWidgets import QScrollArea
        self.scroll_area = QScrollArea() 
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(content_widget)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        return self.scroll_area

    # --- LOGIKA FILTER DASHBOARD (UPDATE) ---
    def filter_dashboard(self, category):
        # Grouping Grafik
        charts_mhs = [self.chart_view, self.gender_chart_view, self.status_chart_view, self.dist_chart_view]
        
        # Update charts_dosen dengan 2 grafik baru
        charts_dosen = [self.jabatan_chart_view, self.dosen_gender_view, self.doswal_chart_view]
        
        charts_prodi = [self.gpa_chart_view]
        
        def set_visible(widgets, visible):
            for w in widgets: w.setVisible(visible)

        if category == "ALL":
            self.welcome_label.setText(f"Selamat Datang, {self.current_username}!")
            self.btn_reset_filter.hide()
            set_visible(charts_mhs, True); set_visible(charts_dosen, True); set_visible(charts_prodi, True)
        else:
            self.btn_reset_filter.show()
            if category == "MAHASISWA":
                self.welcome_label.setText("Analisis Data: MAHASISWA")
                set_visible(charts_mhs, True); set_visible(charts_dosen, False); set_visible(charts_prodi, False)
            elif category == "DOSEN":
                self.welcome_label.setText("Analisis Data: DOSEN")
                set_visible(charts_mhs, False); set_visible(charts_dosen, True); set_visible(charts_prodi, False)
            elif category == "PRODI":
                self.welcome_label.setText("Analisis Data: PROGRAM STUDI")
                set_visible(charts_mhs, False); set_visible(charts_dosen, False); set_visible(charts_prodi, True)

    # --- (Pastikan method ini ada untuk grafik Dosen) ---
    def create_jabatan_dosen_chart(self):
        series = QPieSeries()
        series.setHoleSize(0.35)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Distribusi Jabatan Akademik Dosen")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        # Simpan referensi series agar bisa diupdate datanya
        self.jabatan_series = series 
        return chart_view

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
        self.mhs_page.current_username = username
        self.dosen_page.current_username = username
        self.mk_page.current_username = username
        self.nilai_page.current_username = username
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

class AuditLogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.applyStyles()
        
    def initUI(self):
        # Layout Utama
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Frame Container (Agar mirip "Kartu" seperti widget lain)
        self.container_frame = QFrame()
        self.container_frame.setObjectName("container_frame")
        
        # Layout di dalam Frame
        frame_layout = QVBoxLayout(self.container_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        # --- BAGIAN ATAS: JUDUL & TOMBOL REFRESH ---
        header_layout = QHBoxLayout()
        
        self.label_title = QLabel("Riwayat Aktivitas Sistem")
        self.label_title.setObjectName("title_label")
        
        self.btn_refresh = QPushButton("Refresh Log")
        self.btn_refresh.setObjectName("btn_simpan") # Menggunakan ID style tombol biru
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setFixedWidth(150)
        
        header_layout.addWidget(self.label_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        
        frame_layout.addLayout(header_layout)
        
        # --- BAGIAN TABEL ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Waktu", "User", "Action", "Tabel", "Detail Aktivitas"])
        
        # Setup Header Table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Waktu
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # User
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Action
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Tabel
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Detail (Melar)
        
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        frame_layout.addWidget(self.table)
        
        # Masukkan Frame ke Layout Utama
        main_layout.addWidget(self.container_frame)
        
        # Koneksi Tombol
        self.btn_refresh.clicked.connect(self.load_data)
        
        # Load data pertama kali
        self.load_data()
        
    def applyStyles(self):
        self.setStyleSheet("""
            AuditLogWidget { background-color: #FFFFFF; }
            
            /* Frame Container (Kartu Abu-abu Muda) */
            #container_frame {
                background-color: #F0F2F5;
                border-radius: 10px;
                border: 1px solid #E5E7EB;
            }
            
            /* Judul Halaman */
            #title_label {
                font-size: 20px;
                font-weight: bold;
                color: #2C3E50;
            }
            
            /* Style Tombol (Sama dengan tombol 'Update Data' / 'Simpan') */
            #btn_simpan { 
                background-color: #0078D7; 
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            #btn_simpan:hover { background-color: #005A9E; }
            #btn_simpan:pressed { background-color: #004A8C; }
            
            /* Style Tabel (Putih Bersih) */
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                gridline-color: #E0E0E0;
                color: #000000;
                font-size: 14px;
            }
            
            /* Header Tabel */
            QHeaderView::section {
                background-color: #F7F7F7;
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-size: 14px;
                font-weight: 600;
                color: #000000;
            }
            
            /* Item Tabel saat dipilih */
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: #FFFFFF;
            }
        """)

    def load_data(self):
        if 'SessionLocal' not in globals(): return
        db = SessionLocal()
        try:
            # Ambil 100 log terakhir
            logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
            
            self.table.setRowCount(0)
            for row, log in enumerate(logs):
                self.table.insertRow(row)
                waktu_str = log.timestamp.strftime("%d/%m/%Y %H:%M") if log.timestamp else "-"
                
                # Helper untuk membuat item tabel (read only)
                def create_item(text):
                    item = QTableWidgetItem(str(text))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    return item

                self.table.setItem(row, 0, create_item(waktu_str))
                self.table.setItem(row, 1, create_item(log.username))
                self.table.setItem(row, 2, create_item(log.action))
                self.table.setItem(row, 3, create_item(log.table_name))
                self.table.setItem(row, 4, create_item(log.details))
                
        except Exception as e:
            print(f"Error load log: {e}")
        finally:
            db.close()
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