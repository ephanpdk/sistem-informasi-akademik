from sqlite3 import IntegrityError
import sys
import bcrypt
import pandas as pd
import random 
from collections import defaultdict
from datetime import datetime
import platform
from sqlalchemy import func 

try:
    from database_models import SessionLocal, Pengguna, Mahasiswa, Dosen, Matakuliah, Nilai, AuditLog
except ImportError:
    SessionLocal = None
    pass

from PySide6.QtCore import (
    Qt, Signal, QDate, QSortFilterProxyModel, QMargins, QRect, QSize, 
    QPropertyAnimation, QEasingCurve, QSettings, QPoint
)
from PySide6.QtGui import (
    QIntValidator, QStandardItemModel, QStandardItem, QPainter, QFont, 
    QColor, QPageSize, QPixmap, QIcon, QPalette, QPageLayout
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QMessageBox, QMainWindow, QStackedWidget,
    QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QDateEdit, QComboBox, QFileDialog, QCompleter, 
    QGraphicsDropShadowEffect, QStyleFactory, QScrollArea
)

try:
    from PySide6.QtCharts import (
        QChart, QChartView, QLineSeries, QValueAxis, 
        QScatterSeries, QBarSeries, QBarSet, QBarCategoryAxis,
        QPieSeries, QPieSlice, QStackedBarSeries, QHorizontalBarSeries, QHorizontalStackedBarSeries
    )
except ImportError:
    pass

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    pass
    
try:
    from PySide6.QtPrintSupport import QPrinter
except ImportError:
    pass

def is_system_dark_mode():
    try:
        if sys.platform == "win32":
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
    except:
        pass
    return False 

class ThemeColors:
    def __init__(self, is_dark):
        if is_dark:
            self.BG_MAIN = "#0F172A"     
            self.BG_SIDEBAR = "#020617"   
            self.BG_CARD = "#1E293B"      
            self.TEXT_PRIMARY = "#F1F5F9" 
            self.TEXT_SECONDARY = "#94A3B8" 
            self.BORDER = "#334155"       
            self.INPUT_BG = "#0F172A"
            self.HOVER = "#334155"
            self.TABLE_ALT = "#1E293B"
            self.TABLE_HEAD = "#0F172A"
            self.BTN_TEXT = "#FFFFFF"
            self.CHART_THEME = QChart.ChartThemeDark
        else:
            self.BG_MAIN = "#F4F7F6"      
            self.BG_SIDEBAR = "#1E293B"   
            self.BG_CARD = "#FFFFFF"      
            self.TEXT_PRIMARY = "#334155" 
            self.TEXT_SECONDARY = "#64748B" 
            self.BORDER = "#E2E8F0"       
            self.INPUT_BG = "#FFFFFF"
            self.HOVER = "#F1F5F9"
            self.TABLE_ALT = "#F8FAFC"
            self.TABLE_HEAD = "#F1F5F9"
            self.BTN_TEXT = "#FFFFFF"
            self.CHART_THEME = QChart.ChartThemeLight

        self.ACCENT = "#0EA5E9"     
        self.ACCENT_HOVER = "#0284C7"
        self.DANGER = "#EF4444"     

def get_stylesheet(is_dark):
    c = ThemeColors(is_dark)
    return f"""
    QMainWindow {{ background-color: {c.BG_MAIN}; }}
    QWidget {{ font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 14px; color: {c.TEXT_PRIMARY}; }}
    
    #nav_frame {{ 
        background-color: {c.BG_SIDEBAR}; 
        border-right: 1px solid {c.BORDER};
        min-width: 240px;
        max-width: 240px;
    }}
    #nav_frame QPushButton {{
        color: #94A3B8;
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 14px;
        border-left: 3px solid transparent;
    }}
    #nav_frame QPushButton:hover {{
        background-color: {c.HOVER};
        color: #38BDF8; 
        border-left: 3px solid #38BDF8;
    }}
    
    #content_card, #form_frame, #table_frame, #login_frame {{
        background-color: {c.BG_CARD};
        border-radius: 10px;
        border: 1px solid {c.BORDER};
    }}

    QLineEdit, QDateEdit, QComboBox {{
        border: 1px solid {c.BORDER};
        border-radius: 6px;
        padding: 8px 12px;
        background-color: {c.INPUT_BG};
        color: {c.TEXT_PRIMARY};
    }}
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{
        border: 1px solid {c.ACCENT};
    }}
    
    QTableWidget {{
        border: 1px solid {c.BORDER};
        background-color: {c.BG_CARD};
        gridline-color: {c.BORDER};
        color: {c.TEXT_PRIMARY};
        alternate-background-color: {c.TABLE_ALT};
    }}
    QHeaderView::section {{
        background-color: {c.TABLE_HEAD};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {c.BORDER};
        font-weight: bold;
        color: {c.TEXT_PRIMARY};
    }}
    QTableWidget QTableCornerButton::section {{
        background-color: {c.TABLE_HEAD};
        border: none;
    }}

    QPushButton {{ border-radius: 6px; padding: 8px 16px; font-weight: bold; }}
    
    #btn_simpan, #login_button, #btn_primary {{
        background-color: {c.ACCENT}; color: white; border: none;
    }}
    #btn_simpan:hover, #login_button:hover, #btn_primary:hover {{
        background-color: {c.ACCENT_HOVER};
    }}
    
    #btn_hapus {{
        background-color: {c.DANGER}; color: white; border: none;
    }}
    #btn_hapus:hover {{ background-color: #DC2626; }}
    
    #btn_bersihkan, #btn_export {{
        background-color: transparent; 
        border: 1px solid {c.BORDER};
        color: {c.TEXT_PRIMARY};
    }}
    #btn_bersihkan:hover, #btn_export:hover {{
        background-color: {c.HOVER};
    }}
    """

def log_activity(username, action, table, details):
    if 'SessionLocal' not in globals() or SessionLocal is None: return
    db = SessionLocal()
    try:
        log = AuditLog(username=username, action=action, table_name=table, details=details)
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

def add_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(5)
    shadow.setColor(QColor(0, 0, 0, 40)) 
    widget.setGraphicsEffect(shadow)

class LoginWidget(QWidget):
    login_success_signal = Signal(str, str) 

    def __init__(self, is_dark):
        super().__init__()
        self.is_dark = is_dark
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.card = QFrame()
        self.card.setObjectName("login_frame")
        self.card.setFixedSize(400, 480)
        add_shadow(self.card)
        
        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(40, 50, 40, 50)
        cl.setSpacing(20)
        
        lbl_icon = QLabel("🎓")
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 64px; background: transparent;")
        
        lbl_title = QLabel("SISTEM AKADEMIK")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {'#F1F5F9' if self.is_dark else '#0F172A'}; margin-bottom: 10px;")
        
        self.input_user = QLineEdit(); self.input_user.setPlaceholderText("Username")
        self.input_user.setStyleSheet("padding: 12px;")
        
        self.input_pass = QLineEdit(); self.input_pass.setPlaceholderText("Password")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setStyleSheet("padding: 12px;")
        
        self.btn = QPushButton("MASUK")
        self.btn.setObjectName("login_button")
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet("padding: 12px; font-size: 16px; margin-top: 10px;")
        self.btn.clicked.connect(self.check_login)
        
        cl.addWidget(lbl_icon)
        cl.addWidget(lbl_title)
        cl.addWidget(self.input_user)
        cl.addWidget(self.input_pass)
        cl.addWidget(self.btn)
        cl.addStretch()

        layout.addWidget(self.card)
        self.setLayout(layout)

    def check_login(self):
        u = self.input_user.text()
        p = self.input_pass.text()
        
        if not u or not p:
            QMessageBox.warning(self, "Input", "Isi username dan password!")
            return
            
        if 'SessionLocal' not in globals() or SessionLocal is None:
            QMessageBox.information(self, "Dev Mode", "Database tidak ditemukan. Masuk sebagai DevAdmin.")
            
            self.login_success_signal.emit("DevAdmin", "Admin Manajemen") 
            return

        db = SessionLocal()
        try:
            user = db.query(Pengguna).filter_by(username=u).first()
            if user and bcrypt.checkpw(p.encode(), user.hashed_password.encode()):
                self.login_success_signal.emit(user.username, user.role)
            else:
                QMessageBox.warning(self, "Gagal", "Username/Password Salah")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()

class MahasiswaWidget(QWidget):
    data_changed = Signal()
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.sel_id = None
        self.initUI()
        self.load_data()

    def showEvent(self, event):
        self.load_doswal()
        self.load_data()
        super().showEvent(event)

    def initUI(self):
        layout = QHBoxLayout(self); layout.setContentsMargins(20,20,20,20); layout.setSpacing(20)
        
        self.form_card = QFrame(); self.form_card.setObjectName("form_frame"); self.form_card.setFixedWidth(320)
        add_shadow(self.form_card)
        fl = QVBoxLayout(self.form_card); fl.setContentsMargins(20,20,20,20); fl.setSpacing(15)
        
        fl.addWidget(QLabel("📝 Data Mahasiswa", styleSheet="font-size:18px; font-weight:bold; border:none;"))
        
        f_grid = QFormLayout(); f_grid.setVerticalSpacing(12)
        self.i_nim = QLineEdit(); self.i_nim.setPlaceholderText("NIM")
        self.i_nama = QLineEdit(); self.i_nama.setPlaceholderText("Nama Lengkap")
        self.i_prodi = QLineEdit()
        self.i_gen = QComboBox(); self.i_gen.addItems(["L", "P"])
        self.i_thn = QLineEdit(); self.i_thn.setValidator(QIntValidator(2000,2100))
        self.i_tgl = QDateEdit(); self.i_tgl.setCalendarPopup(True); self.i_tgl.setDisplayFormat("dd/MM/yyyy")
        self.i_stat = QComboBox(); self.i_stat.addItems(["Aktif", "Lulus", "Cuti", "DO"])
        
        self.i_doswal = QComboBox()
        self.i_doswal.setEditable(True)
        self.i_doswal.setInsertPolicy(QComboBox.NoInsert)
        self.i_doswal.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.i_doswal.completer().setFilterMode(Qt.MatchContains)
        
        f_grid.addRow("NIM", self.i_nim); f_grid.addRow("Nama", self.i_nama)
        f_grid.addRow("Prodi", self.i_prodi); f_grid.addRow("L/P", self.i_gen)
        f_grid.addRow("Angkatan", self.i_thn); f_grid.addRow("Tgl Lahir", self.i_tgl)
        f_grid.addRow("Status", self.i_stat); f_grid.addRow("Doswal", self.i_doswal)
        
        fl.addLayout(f_grid); fl.addStretch()
        
        bh = QHBoxLayout()
        b_simpan = QPushButton("Simpan"); b_simpan.setObjectName("btn_simpan"); b_simpan.clicked.connect(self.save)
        b_hapus = QPushButton("Hapus"); b_hapus.setObjectName("btn_hapus"); b_hapus.clicked.connect(self.delete)
        bh.addWidget(b_simpan); bh.addWidget(b_hapus)
        fl.addLayout(bh)
        
        b_rst = QPushButton("Reset Form"); b_rst.setObjectName("btn_bersihkan"); b_rst.clicked.connect(self.reset)
        fl.addWidget(b_rst)
        self.form_card.setEnabled(True)
        
        self.table_card = QFrame(); self.table_card.setObjectName("table_frame")
        add_shadow(self.table_card)
        tl = QVBoxLayout(self.table_card); tl.setContentsMargins(20,20,20,20)
        
        th = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍 Cari Mahasiswa...")
        self.search.textChanged.connect(self.filter)
        
        self.f_prodi = QComboBox()
        self.f_prodi.addItem("Semua Prodi")
        self.f_prodi.currentTextChanged.connect(self.filter)
        
        self.f_tahun = QComboBox()
        self.f_tahun.addItem("Semua Tahun")
        self.f_tahun.currentTextChanged.connect(self.filter)

        b_imp = QPushButton("Import Excel"); b_imp.setObjectName("btn_export"); b_imp.clicked.connect(self.import_xls)
        b_exp = QPushButton("Export Excel"); b_exp.setObjectName("btn_export"); b_exp.clicked.connect(self.export_xls)
        
        th.addWidget(self.search, 2)
        th.addWidget(self.f_prodi, 1)
        th.addWidget(self.f_tahun, 1)
        th.addWidget(b_imp)
        th.addWidget(b_exp)
        tl.addLayout(th)
        
        self.table = QTableWidget(); self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "NIM", "Nama", "Prodi", "L/P", "Thn", "Tgl Lahir", "Status", "Doswal"])
        self.table.setColumnHidden(0, True); self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection) 
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True); self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemClicked.connect(self.row_click)
        tl.addWidget(self.table)
        
        batch_layout = QHBoxLayout()
        self.cb_batch_doswal = QComboBox()
        self.cb_batch_doswal.setEditable(True)
        self.cb_batch_doswal.setInsertPolicy(QComboBox.NoInsert)
        self.cb_batch_doswal.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.cb_batch_doswal.completer().setFilterMode(Qt.MatchContains)
        
        btn_batch = QPushButton("Set Doswal (Batch)")
        btn_batch.setObjectName("btn_simpan")
        btn_batch.clicked.connect(self.batch_update)
        
        batch_layout.addWidget(QLabel("Batch Update Doswal (Pilih Baris):"))
        batch_layout.addWidget(self.cb_batch_doswal, 1)
        batch_layout.addWidget(btn_batch)
        
        tl.addLayout(batch_layout)
        
        layout.addWidget(self.form_card); layout.addWidget(self.table_card)
        self.load_doswal()

    def load_doswal(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        
        self.i_doswal.clear(); self.i_doswal.addItem("-", None)
        self.cb_batch_doswal.clear(); self.cb_batch_doswal.addItem("- Pilih Doswal untuk Batch -", None)
        
        dosen_list = db.query(Dosen).all()
        for d in dosen_list:
            self.i_doswal.addItem(d.nama, d.id)
            self.cb_batch_doswal.addItem(d.nama, d.id)
            
        db.close()

    def load_data(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        try:
            self.table.setRowCount(0)
            list_prodi = set()
            list_tahun = set()

            for i, m in enumerate(db.query(Mahasiswa).all()):
                self.table.insertRow(i)
                self.table.setItem(i,0,QTableWidgetItem(str(m.id)))
                self.table.setItem(i,1,QTableWidgetItem(m.nim))
                self.table.setItem(i,2,QTableWidgetItem(m.nama))
                self.table.setItem(i,3,QTableWidgetItem(m.program_studi))
                self.table.setItem(i,4,QTableWidgetItem(m.gender))
                self.table.setItem(i,5,QTableWidgetItem(str(m.tahun_masuk)))
                self.table.setItem(i,6,QTableWidgetItem(m.tanggal_lahir.strftime("%d/%m/%Y") if m.tanggal_lahir else "-"))
                self.table.setItem(i,7,QTableWidgetItem(m.status))
                self.table.setItem(i,8,QTableWidgetItem(m.dosen_wali.nama if m.dosen_wali else "-"))
                
                if m.program_studi: list_prodi.add(m.program_studi)
                if m.tahun_masuk: list_tahun.add(str(m.tahun_masuk))
            
            current_prodi = self.f_prodi.currentText()
            current_tahun = self.f_tahun.currentText()

            self.f_prodi.blockSignals(True)
            self.f_prodi.clear()
            self.f_prodi.addItem("Semua Prodi")
            self.f_prodi.addItems(sorted(list(list_prodi)))
            self.f_prodi.setCurrentText(current_prodi)
            self.f_prodi.blockSignals(False)

            self.f_tahun.blockSignals(True)
            self.f_tahun.clear()
            self.f_tahun.addItem("Semua Tahun")
            self.f_tahun.addItems(sorted(list(list_tahun)))
            self.f_tahun.setCurrentText(current_tahun)
            self.f_tahun.blockSignals(False)
        finally: db.close()

    def row_click(self, item):
        r = item.row()
        self.sel_id = int(self.table.item(r,0).text())
        self.i_nim.setText(self.table.item(r,1).text())
        self.i_nama.setText(self.table.item(r,2).text())
        self.i_prodi.setText(self.table.item(r,3).text())
        self.i_gen.setCurrentText(self.table.item(r,4).text())
        self.i_thn.setText(self.table.item(r,5).text())
        tgl = self.table.item(r,6).text()
        if tgl != "-": self.i_tgl.setDate(QDate.fromString(tgl, "dd/MM/yyyy"))
        self.i_stat.setCurrentText(self.table.item(r,7).text())
        doswal_name = self.table.item(r,8).text()
        if doswal_name and doswal_name != "-":
            self.i_doswal.setCurrentText(doswal_name)
        else:
            self.i_doswal.setCurrentIndex(0)

    def reset(self):
        self.sel_id = None
        self.i_nim.clear(); self.i_nama.clear(); self.i_prodi.clear(); self.i_thn.clear()
        self.i_doswal.setCurrentIndex(0)

    def save(self):
        db = SessionLocal()
        try:
            nim = self.i_nim.text()
            nama = self.i_nama.text()
            angkatan_str = self.i_thn.text()
            prodi = self.i_prodi.text()
            
            if not nim or len(nim) < 4:
                QMessageBox.warning(self, "Invalid Input", "NIM minimal 4 digit.")
                return
                
            if not angkatan_str:
                QMessageBox.warning(self, "Invalid Input", "Angkatan harus diisi.")
                return

            nim_prefix = nim[:2]
            angkatan_suffix = angkatan_str[-2:]
            
            if nim_prefix != angkatan_suffix:
                QMessageBox.warning(self, "Invalid Input", f"Angkatan invalid! NIM diawali '{nim_prefix}', maka Angkatan harus '20{nim_prefix}'")
                return

            nim_prodi_code = nim[2:4]
            if nim_prodi_code == "01" and prodi.lower() != "sistem informasi":
                QMessageBox.warning(self, "Invalid Input", "Prodi invalid! Kode NIM '01' hanya untuk Prodi 'Sistem Informasi'")
                return

            if not self.sel_id:
                if db.query(Mahasiswa).filter_by(nim=nim).first():
                    QMessageBox.warning(self, "Error", "NIM sudah terdaftar")
                    return
                
                doswal_id = self.i_doswal.currentData()
                if self.i_doswal.currentIndex() < 0:
                    found = self.i_doswal.findText(self.i_doswal.currentText())
                    if found >= 0: doswal_id = self.i_doswal.itemData(found)
                
                new_mhs = Mahasiswa(
                    nim=nim, nama=nama, program_studi=prodi,
                    gender=self.i_gen.currentText(), tahun_masuk=int(angkatan_str),
                    tanggal_lahir=self.i_tgl.date().toPython(), status=self.i_stat.currentText(),
                    dosen_wali_id=doswal_id
                )
                db.add(new_mhs)
                log_activity(self.username, "CREATE", "Mahasiswa", f"Tambah Mhs: {nim} - {nama}")
                QMessageBox.information(self, "Sukses", "Data Berhasil Ditambahkan")
            else:
                existing_mhs = db.query(Mahasiswa).filter_by(nim=nim).first()
                if existing_mhs and existing_mhs.id != self.sel_id:
                    QMessageBox.warning(self, "Error", "NIM sudah digunakan mahasiswa lain")
                    return

                m = db.query(Mahasiswa).get(self.sel_id)
                if m:
                    m.nim = nim
                    m.nama = nama
                    m.program_studi = prodi
                    m.gender = self.i_gen.currentText()
                    m.tahun_masuk = int(angkatan_str)
                    m.tanggal_lahir = self.i_tgl.date().toPython()
                    m.status = self.i_stat.currentText()
                    
                    doswal_id = self.i_doswal.currentData()
                    if self.i_doswal.currentIndex() < 0:
                        found = self.i_doswal.findText(self.i_doswal.currentText())
                        if found >= 0: doswal_id = self.i_doswal.itemData(found)
                    m.dosen_wali_id = doswal_id
                    log_activity(self.username, "UPDATE", "Mahasiswa", f"Update Mhs: {nim} - {nama}")
                    QMessageBox.information(self, "Sukses", "Data Berhasil Diupdate")
            
            db.commit()
            self.load_data()
            self.reset()
            self.data_changed.emit()
        except Exception as e: 
            db.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally: 
            db.close()

    def batch_update(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu mahasiswa dari tabel!")
            return
            
        doswal_id = self.cb_batch_doswal.currentData()
        if self.cb_batch_doswal.currentIndex() < 0:
            found = self.cb_batch_doswal.findText(self.cb_batch_doswal.currentText())
            if found >= 0: doswal_id = self.cb_batch_doswal.itemData(found)
            
        if not doswal_id:
            QMessageBox.warning(self, "Peringatan", "Pilih Dosen Wali untuk Batch Update!")
            return

        if QMessageBox.question(self, "Konfirmasi", f"Update Dosen Wali untuk {len(selected_rows)} mahasiswa terpilih?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.No:
            return

        db = SessionLocal()
        try:
            updated_count = 0
            for row in selected_rows:
                mhs_id = int(self.table.item(row.row(), 0).text())
                mhs = db.query(Mahasiswa).get(mhs_id)
                if mhs:
                    mhs.dosen_wali_id = doswal_id
                    updated_count += 1
            
            if updated_count > 0:
                log_activity(self.username, "BATCH UPDATE", "Mahasiswa", f"Update Doswal untuk {updated_count} Mhs")
                db.commit()
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Sukses", f"Berhasil mengupdate {updated_count} mahasiswa.")
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()

    def delete(self):
        if self.sel_id and QMessageBox.question(self, "Hapus", "Yakin?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                m = db.query(Mahasiswa).get(self.sel_id)
                if m:
                    log_activity(self.username, "DELETE", "Mahasiswa", f"Hapus Mhs: {m.nim} - {m.nama}")
                    db.delete(m)
                    db.commit()
                    self.load_data()
                    self.reset()
                    self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                db.close()

    def filter(self):
        t = self.search.text().lower()
        fp = self.f_prodi.currentText()
        ft = self.f_tahun.currentText()

        for r in range(self.table.rowCount()):
            nim = self.table.item(r,1).text().lower()
            nama = self.table.item(r,2).text().lower()
            prodi = self.table.item(r,3).text()
            tahun = self.table.item(r,5).text()
            
            match_text = t in nim or t in nama
            match_prodi = (fp == "Semua Prodi" or fp == prodi)
            match_tahun = (ft == "Semua Tahun" or ft == tahun)
            self.table.setRowHidden(r, not (match_text and match_prodi and match_tahun))

    def import_xls(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih File Excel", "", "Excel Files (*.xlsx *.xls)")
        if not path: return
        try:
            df = pd.read_excel(path).astype(str)
            df.columns = df.columns.str.strip()
            
            rename_map = {"LP": "Gender", "Thn": "Tahun Masuk", "Tgl": "Tanggal Lahir"}
            df.rename(columns=rename_map, inplace=True)

            req = ["NIM", "Nama", "Prodi", "Gender", "Tahun Masuk", "Status", "Doswal"]
            if not all(col in df.columns for col in req):
                 req_backup = ["NIM", "Nama", "Prodi", "LP", "Thn", "Tgl", "Status", "Doswal"]
                 if all(col in df.columns for col in req_backup):
                     df.rename(columns={"LP":"Gender", "Thn":"Tahun Masuk", "Tgl":"Tanggal Lahir"}, inplace=True)
                 else:
                    QMessageBox.critical(self, "Error", "Format Excel salah. Pastikan kolom: " + ", ".join(req))
                    return
            
            db = SessionLocal()
            dosen_map = {d.nama.strip().lower(): d.id for d in db.query(Dosen).all()}
            
            added, skipped = 0, 0
            for _, r in df.iterrows():
                nim = r["NIM"].strip()
                if not nim or nim.lower() == 'nan' or db.query(Mahasiswa).filter(Mahasiswa.nim==nim).first():
                    skipped += 1; continue
                
                doswal_nama = str(r["Doswal"]).strip()
                doswal_id = None
                for d_name, d_id in dosen_map.items():
                    if d_name in doswal_nama.lower() or doswal_nama.lower() in d_name:
                        doswal_id = d_id
                        break

                tgl_str = str(r.get("Tanggal Lahir", r.get("Tgl", ""))).strip()
                tgl_lahir = None
                try:
                    if tgl_str and tgl_str.lower() != "nan":
                        tgl_lahir = pd.to_datetime(tgl_str).date()
                except: pass

                thn_val = 0
                try: thn_val = int(float(r["Tahun Masuk"]))
                except: pass

                db.add(Mahasiswa(
                    nim=nim,
                    nama=r["Nama"].strip(),
                    program_studi=r["Prodi"].strip(),
                    gender=r["Gender"].strip(),
                    tahun_masuk=thn_val,
                    tanggal_lahir=tgl_lahir,
                    status=r["Status"].strip(),
                    dosen_wali_id=doswal_id
                ))
                added += 1
            
            if added > 0:
                log_activity(self.username, "IMPORT", "Mahasiswa", f"Import {added} data mahasiswa")
            
            db.commit(); db.close(); self.load_data()
            self.data_changed.emit()
            QMessageBox.information(self, "Sukses", f"Import: {added} masuk, {skipped} dilewati.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def export_xls(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File Excel", "export_mahasiswa.xlsx", "Excel Files (*.xlsx)")
        if not path: return
        data = []
        headers = ["NIM", "Nama", "Prodi", "Gender", "Tahun Masuk", "Tanggal Lahir", "Status", "Doswal"]
        for r in range(self.table.rowCount()):
            if not self.table.isRowHidden(r):
                row = [
                    self.table.item(r, 1).text(),
                    self.table.item(r, 2).text(),
                    self.table.item(r, 3).text(),
                    self.table.item(r, 4).text(),
                    self.table.item(r, 5).text(),
                    self.table.item(r, 6).text(),
                    self.table.item(r, 7).text(),
                    self.table.item(r, 8).text()
                ]
                data.append(row)
        try:
            pd.DataFrame(data, columns=headers).to_excel(path, index=False)
            log_activity(self.username, "EXPORT", "Mahasiswa", "Export data mahasiswa ke Excel")
            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke:\n{path}")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

class DosenWidget(QWidget):
    data_changed = Signal()
    JABATAN_LIST = ["Asisten Ahli", "Lektor", "Lektor Kepala", "Profesor"]
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        self.load_data()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)

    def initUI(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(20,20,20,20)
        card = QFrame(); card.setObjectName("table_frame"); add_shadow(card)
        l = QVBoxLayout(card)
        
        th = QHBoxLayout()
        th.addWidget(QLabel("👨‍🏫 Data Dosen", styleSheet="font-size:18px; font-weight:bold"))
        th.addStretch()
        
        b_imp = QPushButton("Import Excel"); b_imp.setObjectName("btn_export"); b_imp.clicked.connect(self.import_xls)
        b_exp = QPushButton("Export Excel"); b_exp.setObjectName("btn_export"); b_exp.clicked.connect(self.export_xls)
        
        th.addWidget(b_imp); th.addWidget(b_exp)
        l.addLayout(th)
        
        self.table = QTableWidget(); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["NIDN", "Nama", "Gender", "Jabatan", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        l.addWidget(self.table)
        layout.addWidget(card)

    def load_data(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        self.table.setRowCount(0)
        for i, d in enumerate(db.query(Dosen).all()):
            self.table.insertRow(i)
            self.table.setItem(i,0,QTableWidgetItem(d.nidn))
            self.table.setItem(i,1,QTableWidgetItem(d.nama))
            self.table.setItem(i,2,QTableWidgetItem(d.gender))
            self.table.setItem(i,3,QTableWidgetItem(d.jabatan_akademik))
            self.table.setItem(i,4,QTableWidgetItem(d.email))
        db.close()

    def import_xls(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih File Excel", "", "Excel Files (*.xlsx *.xls)")
        if not path: return
        try:
            df = pd.read_excel(path).astype(str)
            df.columns = df.columns.str.strip()
            
            req = ["NIDN", "Nama", "Gender", "Jabatan", "Email"]
            if not all(col in df.columns for col in req):
                QMessageBox.critical(self, "Error", "Format Excel salah. Pastikan kolom: " + ", ".join(req))
                return
            
            db = SessionLocal()
            added, skipped = 0, 0
            for _, r in df.iterrows():
                nidn = r["NIDN"].strip()
                email = r["Email"].strip()
                jabatan = r["Jabatan"].strip()
                gender = r["Gender"].strip()
                
                if db.query(Dosen).filter((Dosen.nidn==nidn)|(Dosen.email==email)).first():
                    skipped += 1; continue
                
                if jabatan not in self.JABATAN_LIST or gender not in ['L', 'P']:
                    skipped += 1; continue
                
                db.add(Dosen(nidn=nidn, nama=r["Nama"].strip(), gender=gender, jabatan_akademik=jabatan, email=email))
                added += 1
            
            if added > 0:
                log_activity(self.username, "IMPORT", "Dosen", f"Import {added} data dosen")
            
            db.commit(); db.close(); self.load_data()
            self.data_changed.emit()
            QMessageBox.information(self, "Sukses", f"Import: {added} masuk, {skipped} dilewati.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def export_xls(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File Excel", "export_dosen.xlsx", "Excel Files (*.xlsx)")
        if not path: return
        data = []
        headers = ["NIDN", "Nama", "Gender", "Jabatan", "Email"]
        for r in range(self.table.rowCount()):
            row = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
            data.append(row)
        try:
            pd.DataFrame(data, columns=headers).to_excel(path, index=False)
            log_activity(self.username, "EXPORT", "Dosen", "Export data dosen ke Excel")
            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke:\n{path}")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

class MatakuliahWidget(QWidget):
    data_changed = Signal()
    PRODI_LIST = ["--Pilih Prodi--"]
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.selected_id = None
        self.initUI()
        self.load_data()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)

    def initUI(self):
        layout = QHBoxLayout(self); layout.setContentsMargins(20,20,20,20); layout.setSpacing(20)
        
        self.form_card = QFrame(); self.form_card.setObjectName("form_frame"); self.form_card.setFixedWidth(320)
        add_shadow(self.form_card)
        fl = QVBoxLayout(self.form_card); fl.setContentsMargins(20,20,20,20); fl.setSpacing(15)
        fl.addWidget(QLabel("📚 Matakuliah", styleSheet="font-size:18px; font-weight:bold; border:none;"))
        
        f_grid = QFormLayout(); f_grid.setVerticalSpacing(12)
        self.i_kode = QLineEdit(); self.i_kode.setPlaceholderText("Kode MK")
        self.i_nama = QLineEdit(); self.i_nama.setPlaceholderText("Nama MK")
        self.i_sks = QLineEdit(); self.i_sks.setValidator(QIntValidator(1,9))
        self.i_smt = QLineEdit(); self.i_smt.setValidator(QIntValidator(1,8))
        self.i_prodi = QComboBox(); self.i_prodi.addItems(self.PRODI_LIST)
        
        f_grid.addRow("Kode", self.i_kode); f_grid.addRow("Nama", self.i_nama)
        f_grid.addRow("SKS", self.i_sks); f_grid.addRow("Smt", self.i_smt)
        f_grid.addRow("Prodi", self.i_prodi)
        fl.addLayout(f_grid); fl.addStretch()
        
        bh = QHBoxLayout()
        b_simpan = QPushButton("Simpan"); b_simpan.setObjectName("btn_simpan"); b_simpan.clicked.connect(self.save)
        b_hapus = QPushButton("Hapus"); b_hapus.setObjectName("btn_hapus"); b_hapus.clicked.connect(self.delete)
        bh.addWidget(b_simpan); bh.addWidget(b_hapus)
        fl.addLayout(bh)
        b_rst = QPushButton("Reset"); b_rst.setObjectName("btn_bersihkan"); b_rst.clicked.connect(self.reset)
        fl.addWidget(b_rst); self.form_card.setEnabled(True)

        self.table_card = QFrame(); self.table_card.setObjectName("table_frame")
        add_shadow(self.table_card)
        tl = QVBoxLayout(self.table_card); tl.setContentsMargins(20,20,20,20)
        
        th = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍 Cari MK...")
        self.search.textChanged.connect(self.filter)
        
        self.f_prodi = QComboBox(); self.f_prodi.addItems(["Semua Prodi"] + self.PRODI_LIST[1:])
        self.f_prodi.currentTextChanged.connect(self.filter)
        
        self.f_smt = QComboBox(); self.f_smt.addItems(["Semua Smt"] + [str(i) for i in range(1,9)])
        self.f_smt.currentTextChanged.connect(self.filter)
        
        b_imp = QPushButton("Import Excel"); b_imp.setObjectName("btn_export"); b_imp.clicked.connect(self.import_xls)
        b_exp = QPushButton("Export Excel"); b_exp.setObjectName("btn_export"); b_exp.clicked.connect(self.export_xls)

        th.addWidget(self.search, 2); th.addWidget(self.f_prodi, 1); th.addWidget(self.f_smt, 1)
        th.addWidget(b_imp); th.addWidget(b_exp)
        tl.addLayout(th)

        self.table = QTableWidget(); self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Kode", "Matakuliah", "SKS", "Smt", "Prodi"])
        self.table.setColumnHidden(0, True); self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True); self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers); self.table.itemClicked.connect(self.row_click)
        tl.addWidget(self.table)
        
        layout.addWidget(self.form_card); layout.addWidget(self.table_card)

    def load_data(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        try:
            prodis = db.query(Mahasiswa.program_studi).distinct().all()
            if prodis:
                self.PRODI_LIST = ["--Pilih Prodi--"] + sorted([p[0] for p in prodis if p[0]])
            
            self.i_prodi.clear(); self.i_prodi.addItems(self.PRODI_LIST)
            
            current_f_prodi = self.f_prodi.currentText()
            self.f_prodi.blockSignals(True)
            self.f_prodi.clear(); self.f_prodi.addItems(["Semua Prodi"] + self.PRODI_LIST[1:])
            self.f_prodi.setCurrentText(current_f_prodi)
            self.f_prodi.blockSignals(False)
            
            self.table.setRowCount(0)
            for i, m in enumerate(db.query(Matakuliah).all()):
                self.table.insertRow(i)
                self.table.setItem(i,0,QTableWidgetItem(str(m.id)))
                self.table.setItem(i,1,QTableWidgetItem(m.kode_mk))
                self.table.setItem(i,2,QTableWidgetItem(m.nama_matakuliah))
                self.table.setItem(i,3,QTableWidgetItem(str(m.sks)))
                self.table.setItem(i,4,QTableWidgetItem(str(m.semester)))
                self.table.setItem(i,5,QTableWidgetItem(m.program_studi))
        finally: db.close()

    def row_click(self, item):
        r = item.row()
        self.selected_id = int(self.table.item(r,0).text())
        self.i_kode.setText(self.table.item(r,1).text())
        self.i_nama.setText(self.table.item(r,2).text())
        self.i_sks.setText(self.table.item(r,3).text())
        self.i_smt.setText(self.table.item(r,4).text())
        self.i_prodi.setCurrentText(self.table.item(r,5).text())

    def reset(self):
        self.selected_id = None
        for w in [self.i_kode, self.i_nama, self.i_sks, self.i_smt]: w.clear()
        self.i_prodi.setCurrentIndex(0)

    def save(self):
        db = SessionLocal()
        try:
            kode = self.i_kode.text()
            nama = self.i_nama.text()
            
            if not self.selected_id:
                if db.query(Matakuliah).filter_by(kode_mk=kode).first():
                    QMessageBox.warning(self, "Error", "Kode MK sudah ada")
                    return
                
                db.add(Matakuliah(
                    kode_mk=kode, nama_matakuliah=nama,
                    sks=int(self.i_sks.text()), semester=int(self.i_smt.text()),
                    program_studi=self.i_prodi.currentText()
                ))
                log_activity(self.username, "CREATE", "Matakuliah", f"Tambah MK: {kode} - {nama}")
                QMessageBox.information(self, "Sukses", "Data Disimpan")
            else:
                m = db.query(Matakuliah).get(self.selected_id)
                if m:
                    m.kode_mk = kode
                    m.nama_matakuliah = nama
                    m.sks = int(self.i_sks.text())
                    m.semester = int(self.i_smt.text())
                    m.program_studi = self.i_prodi.currentText()
                    log_activity(self.username, "UPDATE", "Matakuliah", f"Update MK: {kode} - {nama}")
                    QMessageBox.information(self, "Sukses", "Data Diupdate")

            db.commit(); self.load_data(); self.reset()
            self.data_changed.emit()
        except Exception as e: 
            db.rollback(); QMessageBox.critical(self, "Error", str(e))
        finally: db.close()

    def delete(self):
        if self.selected_id and QMessageBox.question(self, "Hapus", "Yakin?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                m = db.query(Matakuliah).get(self.selected_id)
                if m:
                    log_activity(self.username, "DELETE", "Matakuliah", f"Hapus MK: {m.kode_mk}")
                    db.delete(m)
                    db.commit(); self.load_data(); self.reset()
                    self.data_changed.emit()
            except Exception as e: QMessageBox.critical(self, "Error", str(e))
            finally: db.close()

    def filter(self):
        t = self.search.text().lower()
        fp = self.f_prodi.currentText()
        fs = self.f_smt.currentText()
        
        for r in range(self.table.rowCount()):
            kode = self.table.item(r,1).text().lower()
            nama = self.table.item(r,2).text().lower()
            smt = self.table.item(r,4).text()
            prodi = self.table.item(r,5).text()
            
            match = (t in kode or t in nama) and \
                    (fp == "Semua Prodi" or fp == prodi) and \
                    (fs == "Semua Smt" or fs == smt)
            self.table.setRowHidden(r, not match)

    def import_xls(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih File Excel", "", "Excel Files (*.xlsx *.xls)")
        if not path: return
        try:
            df_check = pd.read_excel(path, header=None, nrows=20).astype(str)
            header_row = 0
            for i, row in df_check.iterrows():
                vals = [str(v).strip() for v in row.values]
                if ("Kode MK" in vals or "Kode" in vals) and ("SKS" in vals):
                    header_row = i; break
            
            df = pd.read_excel(path, header=header_row, dtype=str)
            df.columns = df.columns.str.strip()
            
            column_mapping = { "Kode": "Kode MK", "Matakuliah": "Nama Matakuliah", "Smt": "Semester", "Prodi": "Program Studi" }
            df.rename(columns=column_mapping, inplace=True)

            req = ["Kode MK", "Nama Matakuliah", "SKS", "Semester", "Program Studi"]
            if not all(col in df.columns for col in req):
                QMessageBox.critical(self, "Error", "Format Excel salah. Pastikan kolom: " + ", ".join(req))
                return
            
            db = SessionLocal()
            added, skipped = 0, 0
            
            for _, r in df.iterrows():
                kode = str(r["Kode MK"]).strip()
                if not kode or kode.lower() == 'nan' or db.query(Matakuliah).filter(Matakuliah.kode_mk==kode).first():
                    skipped += 1; continue
                
                try:
                    sks_val = int(float(str(r["SKS"]).strip())) if str(r["SKS"]).strip().lower() != 'nan' else 0
                    smt_val = int(float(str(r["Semester"]).strip())) if str(r["Semester"]).strip().lower() != 'nan' else 0
                    nama_mk = str(r["Nama Matakuliah"]).strip(); nama_mk = "" if nama_mk.lower() == 'nan' else nama_mk
                    prodi_mk = str(r["Program Studi"]).strip(); prodi_mk = "" if prodi_mk.lower() == 'nan' else prodi_mk

                    db.add(Matakuliah(kode_mk=kode, nama_matakuliah=nama_mk, sks=sks_val, semester=smt_val, program_studi=prodi_mk))
                    added += 1
                except: skipped += 1
            
            if added > 0:
                log_activity(self.username, "IMPORT", "Matakuliah", f"Import {added} matakuliah")
            
            db.commit(); db.close(); self.load_data()
            self.data_changed.emit()
            QMessageBox.information(self, "Sukses", f"Import: {added} masuk, {skipped} dilewati.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def export_xls(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File Excel", "export_matakuliah.xlsx", "Excel Files (*.xlsx)")
        if not path: return
        data = []
        headers = ["Kode MK", "Nama Matakuliah", "SKS", "Semester", "Program Studi"]
        
        for r in range(self.table.rowCount()):
            if not self.table.isRowHidden(r):
                row = [
                    self.table.item(r, 1).text(),
                    self.table.item(r, 2).text(),
                    self.table.item(r, 3).text(),
                    self.table.item(r, 4).text(),
                    self.table.item(r, 5).text()
                ]
                data.append(row)
        try:
            pd.DataFrame(data, columns=headers).to_excel(path, index=False)
            log_activity(self.username, "EXPORT", "Matakuliah", "Export data matakuliah ke Excel")
            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke:\n{path}")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

class NilaiWidget(QWidget):
    data_changed = Signal()
    NILAI_BOBOT = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.cur_mhs_id = None
        self.cur_prodi = None
        self.mahasiswa_map = {}
        self.all_matakuliah_map = defaultdict(list)
        self.matakuliah_current_map = {}
        self.initUI()
        self.load_initial_data()

    def showEvent(self, event):
        self.load_initial_data()
        if self.cur_mhs_id:
            self.load_transkrip()
        super().showEvent(event)

    def initUI(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(20,20,20,20); layout.setSpacing(20)
        
        top = QFrame(); top.setObjectName("form_frame"); add_shadow(top)
        tl = QHBoxLayout(top); tl.setContentsMargins(20,20,20,20)
        
        self.cb_mhs = QComboBox()
        self.cb_mhs.setEditable(True)
        self.cb_mhs.setInsertPolicy(QComboBox.NoInsert)
        self.cb_mhs.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.cb_mhs.completer().setFilterMode(Qt.MatchContains)
        self.cb_mhs.activated.connect(self.mahasiswa_dipilih)
        
        self.lbl_ipk = QLabel("IPK: -", styleSheet="font-size:16px; font-weight:bold; color:#0EA5E9")
        tl.addWidget(QLabel("Pilih Mahasiswa:")); tl.addWidget(self.cb_mhs, 2); tl.addStretch(); tl.addWidget(self.lbl_ipk)
        
        mid = QFrame(); mid.setObjectName("form_frame"); add_shadow(mid)
        ml = QHBoxLayout(mid)
        self.cb_mk = QComboBox(); self.cb_mk.setEditable(True)
        self.cb_smt = QComboBox(); self.cb_smt.addItems(["- Smt -"] + [str(i) for i in range(1,9)])
        self.cb_smt.currentTextChanged.connect(self.update_mk_dropdown)
        
        self.cb_nil = QComboBox(); self.cb_nil.addItems(["A","B","C","D","E"])
        
        b_add = QPushButton("Simpan Nilai"); b_add.setObjectName("btn_simpan"); b_add.clicked.connect(self.simpan_nilai)
        b_del = QPushButton("Hapus"); b_del.setObjectName("btn_hapus"); b_del.clicked.connect(self.hapus_nilai)
        
        b_dummy = QPushButton("Generate Full Dummy"); b_dummy.setObjectName("btn_export"); b_dummy.clicked.connect(self.generate_dummy)
        
        ml.addWidget(self.cb_smt); ml.addWidget(self.cb_mk, 2); ml.addWidget(self.cb_nil)
        ml.addWidget(b_add); ml.addWidget(b_del); ml.addWidget(b_dummy)
        
        bot = QFrame(); bot.setObjectName("table_frame"); add_shadow(bot)
        bl = QVBoxLayout(bot)
        self.table = QTableWidget(); self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Smt", "Kode", "Matakuliah", "SKS", "Nilai", "Bobot"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemClicked.connect(self.row_click)
        
        b_pdf = QPushButton("Cetak Transkrip (PDF)"); b_pdf.setObjectName("btn_simpan"); b_pdf.clicked.connect(self.print_transkrip)
        
        bl.addWidget(self.table); bl.addWidget(b_pdf)
        
        layout.addWidget(top); layout.addWidget(mid); layout.addWidget(bot)

    def load_initial_data(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        try:
            current_mhs_text = self.cb_mhs.currentText()
            self.cb_mhs.clear()
            self.mahasiswa_map = {}
            
            model = QStandardItemModel()
            model.appendRow(QStandardItem("- Pilih Mahasiswa -"))

            for m in db.query(Mahasiswa).filter_by(status='Aktif').all():
                txt = f"{m.nim} - {m.nama}"
                self.mahasiswa_map[txt] = {"id": m.id, "prodi": m.program_studi}
                model.appendRow(QStandardItem(txt))
            
            self.cb_mhs.setModel(model)
            self.cb_mhs.setModelColumn(0)
            
            if current_mhs_text in self.mahasiswa_map:
                self.cb_mhs.setCurrentText(current_mhs_text)

            self.all_matakuliah_map = defaultdict(list)
            for mk in db.query(Matakuliah).all():
                key = (str(mk.semester), mk.program_studi)
                disp = f"{mk.kode_mk} - {mk.nama_matakuliah}"
                self.all_matakuliah_map[key].append((disp, {"id": mk.id, "sks": mk.sks}))
        finally:
            db.close()

    def row_click(self, item):
        row = item.row()
        try:
            nid = int(self.table.item(row, 0).text())
            db = SessionLocal()
            nilai = db.query(Nilai).get(nid)
            
            if nilai and nilai.matakuliah:
                mk = nilai.matakuliah
                
                self.cb_smt.setCurrentText(str(mk.semester))
                self.update_mk_dropdown()
                
                mk_text = f"{mk.kode_mk} - {mk.nama_matakuliah}"
                self.cb_mk.setCurrentText(mk_text)
                
                self.cb_nil.setCurrentText(nilai.nilai_huruf)
                
            db.close()
        except Exception as e:
            print(f"Row click error: {e}")

    def generate_dummy(self):
        db = SessionLocal()
        try:
            mhs_list = db.query(Mahasiswa).filter_by(status='Aktif').all()
            mk_list = db.query(Matakuliah).all()
            
            if not mhs_list or not mk_list:
                QMessageBox.warning(self, "Error", "Data Mahasiswa atau Matakuliah kosong.")
                return

            existing_grades = set()
            for n in db.query(Nilai.mahasiswa_id, Nilai.matakuliah_id).all():
                existing_grades.add((n.mahasiswa_id, n.matakuliah_id))

            added_count = 0
            
            for mhs in mhs_list:
                for mk in mk_list:
                    if mhs.program_studi == mk.program_studi:
                        if (mhs.id, mk.id) not in existing_grades:
                            huruf = random.choice(["A", "B", "C"])
                            angka = self.NILAI_BOBOT[huruf]
                            
                            new_nilai = Nilai(
                                mahasiswa_id=mhs.id,
                                matakuliah_id=mk.id,
                                nilai_huruf=huruf,
                                nilai_angka=angka,
                                semester_diambil=mk.semester
                            )
                            db.add(new_nilai)
                            added_count += 1
            
            db.commit()
            if added_count > 0:
                log_activity(self.username, "CREATE", "Nilai", f"Generate {added_count} Nilai Dummy Massal")
                self.data_changed.emit()
                QMessageBox.information(self, "Sukses", f"Berhasil mengisi {added_count} nilai kosong.")
                if self.cur_mhs_id: self.load_transkrip()
            else:
                QMessageBox.information(self, "Info", "Semua mahasiswa sudah memiliki nilai lengkap.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()

    def mahasiswa_dipilih(self):
        txt = self.cb_mhs.currentText()
        data = self.mahasiswa_map.get(txt)
        if data:
            self.cur_mhs_id = data["id"]
            self.cur_prodi = data["prodi"]
            self.load_transkrip()
            self.cb_smt.setCurrentIndex(0)
            self.cb_mk.clear()
        else:
            self.cur_mhs_id = None
            self.cur_prodi = None
            self.table.setRowCount(0)
            self.lbl_ipk.setText("IPK: -")

    def update_mk_dropdown(self):
        self.cb_mk.clear()
        self.matakuliah_current_map = {}
        smt = self.cb_smt.currentText()
        
        if not self.cur_prodi or smt == "- Smt -": return

        mks = self.all_matakuliah_map.get((smt, self.cur_prodi), [])
        for name, data in mks:
            self.matakuliah_current_map[name] = data
            self.cb_mk.addItem(name)

    def load_transkrip(self):
        if not self.cur_mhs_id: return
        db = SessionLocal()
        try:
            rows = db.query(Nilai, Matakuliah).join(Matakuliah).filter(Nilai.mahasiswa_id == self.cur_mhs_id).order_by(Nilai.semester_diambil).all()
            self.table.setRowCount(0)
            tsks = 0; tbobot = 0
            
            for i, (n, mk) in enumerate(rows):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(n.id)))
                self.table.setItem(i, 1, QTableWidgetItem(str(n.semester_diambil)))
                self.table.setItem(i, 2, QTableWidgetItem(mk.kode_mk))
                self.table.setItem(i, 3, QTableWidgetItem(mk.nama_matakuliah))
                self.table.setItem(i, 4, QTableWidgetItem(str(mk.sks)))
                self.table.setItem(i, 5, QTableWidgetItem(n.nilai_huruf))
                self.table.setItem(i, 6, QTableWidgetItem(str(n.nilai_angka)))
                
                tsks += mk.sks
                tbobot += (n.nilai_angka * mk.sks)
            
            ipk = tbobot / tsks if tsks > 0 else 0.0
            self.lbl_ipk.setText(f"Total SKS: {tsks} | IPK: {ipk:.2f}")
        finally:
            db.close()

    def simpan_nilai(self):
        if not self.cur_mhs_id: return
        mk_txt = self.cb_mk.currentText()
        if not mk_txt or mk_txt not in self.matakuliah_current_map:
            QMessageBox.warning(self, "Error", "Pilih Matakuliah valid"); return

        mk_id = self.matakuliah_current_map[mk_txt]["id"]
        hrf = self.cb_nil.currentText()
        angka = self.NILAI_BOBOT[hrf]
        smt = int(self.cb_smt.currentText())

        db = SessionLocal()
        try:
            exist = db.query(Nilai).filter_by(mahasiswa_id=self.cur_mhs_id, matakuliah_id=mk_id).first()
            if exist:
                if QMessageBox.question(self, "Update", "Nilai sudah ada. Update?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                    exist.nilai_huruf = hrf
                    exist.nilai_angka = angka
                    log_activity(self.username, "UPDATE", "Nilai", f"Mhs {self.cur_mhs_id} MK {mk_id} -> {hrf}")
                    db.commit()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Sukses", "Nilai Diupdate")
            else:
                db.add(Nilai(mahasiswa_id=self.cur_mhs_id, matakuliah_id=mk_id, nilai_huruf=hrf, nilai_angka=angka, semester_diambil=smt))
                log_activity(self.username, "CREATE", "Nilai", f"Mhs {self.cur_mhs_id} MK {mk_id} -> {hrf}")
                db.commit()
                self.data_changed.emit()
                QMessageBox.information(self, "Sukses", "Nilai Disimpan")
            self.load_transkrip()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()

    def hapus_nilai(self):
        row = self.table.currentRow()
        if row < 0: QMessageBox.warning(self, "Error", "Pilih nilai di tabel"); return
        
        nid = int(self.table.item(row, 0).text())
        if QMessageBox.question(self, "Hapus", "Yakin hapus nilai ini?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                obj = db.query(Nilai).get(nid)
                if obj:
                    db.delete(obj)
                    log_activity(self.username, "DELETE", "Nilai", f"ID {nid}")
                    db.commit()
                    self.data_changed.emit()
                    self.load_transkrip()
            finally:
                db.close()

    def print_transkrip(self):
        if not self.cur_mhs_id: return
        db = SessionLocal()
        mhs = db.query(Mahasiswa).get(self.cur_mhs_id)
        doswal_nama = mhs.dosen_wali.nama if mhs.dosen_wali else "-"
        vals = db.query(Nilai, Matakuliah).join(Matakuliah).filter(Nilai.mahasiswa_id==mhs.id).order_by(Nilai.semester_diambil).all()
        db.close()

        path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", f"Transkrip_{mhs.nim}.pdf", "*.pdf")
        if not path: return

        doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("TRANSKRIP AKADEMIK", styles['Title']))
        elements.append(Spacer(1, 20))

        info = [
            [Paragraph("<b>Nama</b>", styles["Normal"]), ": " + mhs.nama, Paragraph("<b>Prodi</b>", styles["Normal"]), ": " + mhs.program_studi],
            [Paragraph("<b>NIM</b>", styles["Normal"]), ": " + mhs.nim, Paragraph("<b>Thn Masuk</b>", styles["Normal"]), ": " + str(mhs.tahun_masuk)],
            [Paragraph("<b>Dosen Wali</b>", styles["Normal"]), ": " + doswal_nama, "", ""]
        ]
        t_info = Table(info, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 2.5*inch])
        t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(t_info); elements.append(Spacer(1, 20))

        data = [['No', 'Smt', 'Kode', 'Matakuliah', 'SKS', 'Nilai', 'Bobot']]
        tsks = 0; tpoin = 0
        for i, (n, mk) in enumerate(vals, 1):
            bot = n.nilai_angka * mk.sks
            tsks += mk.sks; tpoin += bot
            data.append([str(i), str(n.semester_diambil), mk.kode_mk, Paragraph(mk.nama_matakuliah, styles["BodyText"]), str(mk.sks), n.nilai_huruf, f"{n.nilai_angka:.2f}"])

        ipk = tpoin/tsks if tsks > 0 else 0
        t = Table(data, colWidths=[0.4*inch, 0.5*inch, 1.0*inch, 2.8*inch, 0.5*inch, 0.6*inch, 0.6*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (3,1), (3,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t); elements.append(Spacer(1, 20))

        sum_data = [
            ["Total SKS", f": {tsks}"],
            ["IPK", f": {ipk:.2f}"],
            ["Predikat", f": {'Cum Laude' if ipk > 3.5 else 'Sangat Memuaskan' if ipk > 3.0 else 'Memuaskan'}"]
        ]
        elements.append(Table(sum_data, hAlign='LEFT'))
        
        elements.append(Spacer(1, 30))
        tgl_cetak = datetime.now().strftime("%d %B %Y")
        ttd_data = [
            [Paragraph(f"Dicetak pada: {tgl_cetak}", styles["Normal"])],
            [Spacer(1, 30)],
            [Paragraph("( ........................... )", styles["Normal"])]
        ]
        t_ttd = Table(ttd_data, hAlign='RIGHT')
        elements.append(t_ttd)
        
        try:
            doc.build(elements)
            log_activity(self.username, "EXPORT", "Transkrip", f"PDF {mhs.nim}")
            QMessageBox.information(self, "Sukses", "Transkrip Disimpan")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class PenggunaWidget(QWidget):
    ROLE_LIST = ["Admin Manajemen", "Admin Akademik"]
    
    def __init__(self, username): 
        super().__init__()
        self.current_username = username 
        self.selected_pengguna_id = None
        self.initUI()
        self.load_data()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.form_card = QFrame()
        self.form_card.setObjectName("form_frame")
        self.form_card.setFixedWidth(320)
        add_shadow(self.form_card)
        
        fl = QVBoxLayout(self.form_card)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(15)
        
        fl.addWidget(QLabel("👤 Manajemen Pengguna", styleSheet="font-size:18px; font-weight:bold; border:none;"))

        f_grid = QFormLayout()
        f_grid.setVerticalSpacing(12)
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Isi untuk ubah/buat baru")
        
        self.input_role = QComboBox()
        self.input_role.addItems(self.ROLE_LIST)

        f_grid.addRow("Username", self.input_username)
        f_grid.addRow("Password", self.input_password)
        f_grid.addRow("Role", self.input_role)
        
        fl.addLayout(f_grid)
        fl.addStretch()

        bh = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.setObjectName("btn_simpan")
        self.btn_simpan.clicked.connect(self.save_data)
        
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_hapus")
        self.btn_hapus.clicked.connect(self.delete_data)
        
        bh.addWidget(self.btn_simpan)
        bh.addWidget(self.btn_hapus)
        fl.addLayout(bh)

        self.btn_bersihkan = QPushButton("Reset Form")
        self.btn_bersihkan.setObjectName("btn_bersihkan")
        self.btn_bersihkan.clicked.connect(self.clear_form)
        fl.addWidget(self.btn_bersihkan)

        self.table_card = QFrame()
        self.table_card.setObjectName("table_frame")
        add_shadow(self.table_card)
        
        tl = QVBoxLayout(self.table_card)
        tl.setContentsMargins(20, 20, 20, 20)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari berdasarkan Username atau Role...")
        self.search_input.textChanged.connect(self.filter_table)
        tl.addWidget(self.search_input)

        self.table_pengguna = QTableWidget()
        self.table_pengguna.setColumnCount(4)
        self.table_pengguna.setHorizontalHeaderLabels(["#", "ID", "Username", "Role"])
        self.table_pengguna.verticalHeader().hide()
        self.table_pengguna.setColumnHidden(1, True)
        self.table_pengguna.setColumnWidth(0, 50)
        self.table_pengguna.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_pengguna.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_pengguna.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_pengguna.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_pengguna.setAlternatingRowColors(True)
        self.table_pengguna.itemClicked.connect(self.table_row_clicked)
        
        tl.addWidget(self.table_pengguna)

        layout.addWidget(self.form_card)
        layout.addWidget(self.table_card)

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
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db_session = SessionLocal()
        try:
            semua_pengguna = db_session.query(Pengguna).all()
            self.table_pengguna.setRowCount(0) 
            for row_position, user in enumerate(semua_pengguna):
                self.table_pengguna.insertRow(row_position)
                
                nomor_item = QTableWidgetItem(str(row_position + 1))
                nomor_item.setTextAlignment(Qt.AlignCenter)
                
                self.table_pengguna.setItem(row_position, 0, nomor_item) 
                self.table_pengguna.setItem(row_position, 1, QTableWidgetItem(str(user.id)))
                self.table_pengguna.setItem(row_position, 2, QTableWidgetItem(user.username))
                self.table_pengguna.setItem(row_position, 3, QTableWidgetItem(user.role))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {e}")
        finally:
            db_session.close()

    def save_data(self):
        username = self.input_username.text()
        password = self.input_password.text() 
        role = self.input_role.currentText()
        
        if not username:
            QMessageBox.warning(self, "Error", "Username tidak boleh kosong.")
            return
            
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db_session = SessionLocal()
        
        try:
            if self.selected_pengguna_id:
                user = db_session.query(Pengguna).get(self.selected_pengguna_id)
                if user:
                    if user.username != username:
                        username_ada = db_session.query(Pengguna).filter_by(username=username).first()
                        if username_ada:
                            QMessageBox.warning(self, "Error", f"Username '{username}' sudah terdaftar.")
                            return
                    
                    if password:
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        user.hashed_password = hashed_password.decode('utf-8')
                    
                    user.username = username
                    user.role = role
                    log_activity(self.current_username, "UPDATE", "Pengguna", f"Update User: {username}")
                    QMessageBox.information(self, "Sukses", "Data berhasil diperbarui.")
            
            else:
                if not password:
                    QMessageBox.warning(self, "Error", "Password wajib diisi untuk pengguna baru.")
                    return
                
                username_ada = db_session.query(Pengguna).filter_by(username=username).first()
                if username_ada:
                    QMessageBox.warning(self, "Error", f"Username '{username}' sudah terdaftar.")
                    return
                
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user_baru = Pengguna(
                    username=username,
                    hashed_password=hashed_password.decode('utf-8'),
                    role=role
                )
                db_session.add(user_baru)
                log_activity(self.current_username, "CREATE", "Pengguna", f"Buat User: {username}")
                QMessageBox.information(self, "Sukses", "Pengguna berhasil dibuat.")
            
            db_session.commit()
            self.load_data()
            self.clear_form()
            
        except Exception as e:
            db_session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db_session.close()

    def delete_data(self):
        if not self.selected_pengguna_id:
            QMessageBox.warning(self, "Error", "Pilih pengguna yang ingin dihapus.")
            return
            
        row = self.table_pengguna.currentRow()
        username_to_delete = self.table_pengguna.item(row, 2).text()
        
        if username_to_delete == "admin":
            QMessageBox.warning(self, "Error", "Akun 'admin' utama tidak boleh dihapus.")
            return
        if username_to_delete == self.current_username:
            QMessageBox.warning(self, "Error", "Anda tidak dapat menghapus akun sendiri.")
            return
            
        if QMessageBox.question(self, "Hapus", f"Yakin hapus user '{username_to_delete}'?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db_session = SessionLocal()
            try:
                user = db_session.query(Pengguna).get(self.selected_pengguna_id)
                if user:
                    db_session.delete(user)
                    log_activity(self.current_username, "DELETE", "Pengguna", f"Hapus User: {username_to_delete}")
                    db_session.commit()
                    self.load_data()
                    self.clear_form()
            except Exception as e:
                db_session.rollback()
                QMessageBox.critical(self, "Error", str(e))
            finally:
                db_session.close()

    def clear_form(self):
        self.selected_pengguna_id = None 
        self.input_username.clear()
        self.input_password.clear()
        self.input_role.setCurrentIndex(0) 
        self.input_username.setReadOnly(False)
        self.input_password.setPlaceholderText("Isi untuk ubah/buat baru")

    def table_row_clicked(self, item):
        row = item.row()
        self.selected_pengguna_id = int(self.table_pengguna.item(row, 1).text())
        username = self.table_pengguna.item(row, 2).text()
        role = self.table_pengguna.item(row, 3).text()
        
        self.input_username.setText(username)
        self.input_role.setCurrentText(role)
        self.input_password.clear()
        self.input_password.setPlaceholderText("Kosongkan jika tidak ingin mengubah password")
        
        if username == "admin":
            self.input_username.setReadOnly(True)
        else:
            self.input_username.setReadOnly(False)

class AuditLogWidget(QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.initUI()
        self.load_data()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        card = QFrame()
        card.setObjectName("table_frame")
        add_shadow(card)
        
        l = QVBoxLayout(card)
        
        hl = QHBoxLayout()
        hl.addWidget(QLabel("📜 Log Aktivitas", styleSheet="font-size:18px; font-weight:bold"))
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setObjectName("btn_export")
        btn_refresh.clicked.connect(self.load_data)
        
        hl.addStretch()
        hl.addWidget(btn_refresh)

        if self.role == "Admin Manajemen":
            btn_del_sel = QPushButton("Hapus Baris")
            btn_del_sel.setObjectName("btn_hapus")
            btn_del_sel.clicked.connect(self.delete_selected)
            hl.addWidget(btn_del_sel)

            btn_clear = QPushButton("Hapus Semua")
            btn_clear.setObjectName("btn_hapus")
            btn_clear.clicked.connect(self.clear_all_logs)
            hl.addWidget(btn_clear)

        l.addLayout(hl)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Waktu", "User", "Aksi", "Detail"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        l.addWidget(self.table)
        
        layout.addWidget(card)

    def load_data(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        try:
            self.table.setRowCount(0)
            logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
            for i, lg in enumerate(logs):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(lg.id)))
                self.table.setItem(i, 1, QTableWidgetItem(lg.timestamp.strftime("%d/%m %H:%M")))
                self.table.setItem(i, 2, QTableWidgetItem(lg.username))
                self.table.setItem(i, 3, QTableWidgetItem(f"{lg.action} - {lg.table_name}"))
                self.table.setItem(i, 4, QTableWidgetItem(lg.details))
        finally:
            db.close()

    def delete_selected(self):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        if not rows:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang akan dihapus")
            return

        if QMessageBox.question(self, "Konfirmasi", f"Hapus {len(rows)} baris log?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        db = SessionLocal()
        try:
            for r in rows:
                log_id = int(self.table.item(r, 0).text())
                obj = db.query(AuditLog).get(log_id)
                if obj:
                    db.delete(obj)
            db.commit()
            log_activity(self.username, "DELETE", "AuditLog", f"Menghapus {len(rows)} baris log")
            self.load_data()
            QMessageBox.information(self, "Sukses", "Log terpilih berhasil dihapus")
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()

    def clear_all_logs(self):
        if QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus SELURUH riwayat log?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db = SessionLocal()
            try:
                db.query(AuditLog).delete()
                db.commit()
                log_activity(self.username, "DELETE", "AuditLog", "Menghapus seluruh history log")
                self.load_data()
                QMessageBox.information(self, "Sukses", "Seluruh log berhasil dihapus")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Error", str(e))
            finally:
                db.close()

class MainWidget(QWidget):
    logout_signal = Signal()
    def __init__(self, username, role, is_dark):
        super().__init__()
        self.username = username
        self.role = role
        self.is_dark = is_dark
        
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.dashboard = self.create_dashboard()
        
        self.mhs_page = MahasiswaWidget(username)
        self.dosen_page = DosenWidget(username)
        self.mk_page = MatakuliahWidget(username)
        self.nilai_page = NilaiWidget(username)
        self.audit_page = AuditLogWidget(username, role)
        self.user_page = PenggunaWidget(username)
        
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.mhs_page)
        self.stack.addWidget(self.dosen_page)
        self.stack.addWidget(self.mk_page)
        self.stack.addWidget(self.nilai_page)
        self.stack.addWidget(self.audit_page)
        self.stack.addWidget(self.user_page)
        
        self.mhs_page.data_changed.connect(self.update_dashboard_stats)
        self.dosen_page.data_changed.connect(self.update_dashboard_stats)
        self.mk_page.data_changed.connect(self.update_dashboard_stats)
        self.nilai_page.data_changed.connect(self.update_dashboard_stats)

        self.nav = self.create_nav()
        layout.addWidget(self.nav)
        layout.addWidget(self.stack)

        self.update_dashboard_stats()

    def create_nav(self):
        f = QFrame(); f.setObjectName("nav_frame")
        l = QVBoxLayout(f); l.setContentsMargins(0,0,0,0); l.setSpacing(5)
        
        l.addWidget(QLabel("🎓 SIAKAD", objectName="app_logo", alignment=Qt.AlignCenter))
        
        def btn(txt, idx):
            b = QPushButton(txt); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda: self.stack.setCurrentIndex(idx))
            return b
        
        l.addWidget(btn("🏠 Dashboard", 0))

        if self.role == "Admin Manajemen":
            l.addWidget(btn("🎓 Mahasiswa", 1))
            l.addWidget(btn("👨‍🏫 Dosen", 2))
            l.addWidget(btn("📚 Matakuliah", 3))
            l.addWidget(btn("👤 Pengguna", 6))
            l.addWidget(btn("📜 Log Sistem", 5))
            
        elif self.role == "Admin Akademik":
            l.addWidget(btn("📝 Penilaian", 4))
        
        else:
             l.addWidget(btn("🎓 Mahasiswa", 1))
             l.addWidget(btn("👨‍🏫 Dosen", 2))
             l.addWidget(btn("📚 Matakuliah", 3))
             l.addWidget(btn("📝 Penilaian", 4))
             l.addWidget(btn("📜 Log Sistem", 5))
             l.addWidget(btn("👤 Pengguna", 6))

        l.addStretch()
        
        bout = QPushButton("🚪 Logout")
        bout.setStyleSheet("text-align:left; padding:15px; color:#EF4444; background:transparent; border:none; font-weight:bold")
        bout.clicked.connect(lambda: self.logout_signal.emit())
        l.addWidget(bout)
        
        return f
    
    def create_dashboard(self):
        from PySide6.QtWidgets import QTabWidget, QScrollArea
        
        base_widget = QWidget()
        base_layout = QVBoxLayout(base_widget)
        base_layout.setContentsMargins(30,30,30,30); base_layout.setSpacing(20)

        head_layout = QHBoxLayout()
        color = "#F1F5F9" if self.is_dark else "#1E293B"
        head_layout.addWidget(QLabel(f"👋 Selamat Datang, {self.username} ({self.role})", styleSheet=f"font-size:28px; font-weight:800; color:{color}"))
        btn_pdf = QPushButton("Export PDF")
        btn_pdf.setObjectName("btn_simpan")
        btn_pdf.clicked.connect(self.export_dashboard_pdf)
        head_layout.addStretch()
        head_layout.addWidget(btn_pdf)
        base_layout.addLayout(head_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { font-size: 14px; font-weight: bold; padding: 10px 20px; margin-right: 5px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
            QTabBar::tab:selected { background: #3B82F6; color: white; }
            QTabBar::tab:!selected { background: #E2E8F0; color: #64748B; }
        """)

        self.tab_overview = QWidget()
        self.tab_academic = QWidget()
        self.tab_faculty = QWidget()

        self.setup_tab_overview()
        self.setup_tab_academic()
        self.setup_tab_faculty()

        self.tabs.addTab(self.tab_overview, "📊 Ringkasan Eksekutif")
        self.tabs.addTab(self.tab_academic, "📚 Intelijen Akademik")
        self.tabs.addTab(self.tab_faculty, "👨‍🏫 Analisis Fakultas")

        base_layout.addWidget(self.tabs)
        return base_widget

    def setup_tab_overview(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        l = QVBoxLayout(content); l.setSpacing(30); l.setContentsMargins(10,10,10,10)

        cards = QHBoxLayout(); cards.setSpacing(25)
        self.lbl_mhs = QLabel("0"); self.lbl_dsn = QLabel("0"); self.lbl_prodi = QLabel("0"); self.lbl_kritis = QLabel("0")
        
        def card(ico, lbl_obj, txt, col_bg, col_accent):
            c = QFrame(); c.setFixedSize(240, 110)
            c.setStyleSheet(f"QFrame {{ background-color: {col_bg}; border-radius: 12px; border-left: 5px solid {col_accent}; }}")
            add_shadow(c)
            ml = QHBoxLayout(c); ml.setContentsMargins(20, 15, 20, 15)
            il = QVBoxLayout(); il.setSpacing(5)
            lbl_txt = QLabel(txt); lbl_txt.setStyleSheet(f"color: #64748B; font-size: 12px; font-weight: 600; border: none; background: transparent;")
            lbl_obj.setStyleSheet(f"color: #1E293B; font-size: 24px; font-weight: 800; border: none; background: transparent;")
            il.addWidget(lbl_txt); il.addWidget(lbl_obj)
            icon_lbl = QLabel(ico); icon_lbl.setStyleSheet(f"font-size: 36px; color: {col_accent}; border: none; background: transparent; opacity: 0.8;")
            icon_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            ml.addLayout(il); ml.addWidget(icon_lbl)
            return c

        cards.addWidget(card("🎓", self.lbl_mhs, "TOTAL MAHASISWA", "#FFFFFF", "#3B82F6"))
        cards.addWidget(card("👨‍🏫", self.lbl_dsn, "TOTAL DOSEN", "#FFFFFF", "#10B981"))
        cards.addWidget(card("🏛️", self.lbl_prodi, "PROGRAM STUDI", "#FFFFFF", "#F59E0B"))
        cards.addWidget(card("⚠️", self.lbl_kritis, "IPK < 2.0 (KRITIS)", "#FFFFFF", "#EF4444"))
        l.addLayout(cards)

        self.chart_trend = self.create_chart_container("Tren Pertumbuhan Mahasiswa")
        l.addWidget(self.chart_trend)

        self.chart_ipk_trend = self.create_chart_container("Tren Rata-rata IPK per Angkatan")
        l.addWidget(self.chart_ipk_trend)

        self.chart_status = self.create_chart_container("Distribusi Status Mahasiswa")
        l.addWidget(self.chart_status)

        l.addStretch()
        scroll.setWidget(content)
        layout = QVBoxLayout(self.tab_overview); layout.setContentsMargins(0,0,0,0); layout.addWidget(scroll)

    def setup_tab_academic(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        l = QVBoxLayout(content); l.setSpacing(30); l.setContentsMargins(10,10,10,10)

        r1 = QHBoxLayout()
        self.chart_dist = self.create_chart_container("Sebaran IPK Mahasiswa")
        self.chart_mk_fail = self.create_chart_container("Matakuliah Terberat (Nilai D/E Terbanyak)")
        r1.addWidget(self.chart_dist); r1.addWidget(self.chart_mk_fail)
        l.addLayout(r1)

        self.chart_gpa_prodi_year = self.create_chart_container("Analisis IPK per Program Studi")
        l.addWidget(self.chart_gpa_prodi_year)

        r3 = QHBoxLayout()
        def create_table_box(title):
            f = QFrame(); f.setObjectName("content_card"); f.setMinimumHeight(300)
            add_shadow(f)
            v = QVBoxLayout(f)
            lbl = QLabel(title, styleSheet="font-size:16px; font-weight:bold; margin-bottom:10px; border:none;")
            v.addWidget(lbl)
            t = QTableWidget()
            t.verticalHeader().hide()
            t.setAlternatingRowColors(True)
            t.setEditTriggers(QTableWidget.NoEditTriggers)
            v.addWidget(t)
            return f, t

        self.box_top10, self.table_top10 = create_table_box("🏆 Top 10 Mahasiswa Berprestasi")
        self.box_late, self.table_late = create_table_box("⏳ Mahasiswa > 5 Tahun")
        r3.addWidget(self.box_top10); r3.addWidget(self.box_late)
        l.addLayout(r3)

        l.addStretch()
        scroll.setWidget(content)
        layout = QVBoxLayout(self.tab_academic); layout.setContentsMargins(0,0,0,0); layout.addWidget(scroll)

    def setup_tab_faculty(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        l = QVBoxLayout(content); l.setSpacing(30); l.setContentsMargins(10,10,10,10)

        r1 = QHBoxLayout()
        self.chart_gender = self.create_chart_container("Demografi Gender per Prodi")
        self.chart_doswal_perf = self.create_chart_container("Kinerja Dosen Wali (Rata-rata IPK Bimbingan)")
        r1.addWidget(self.chart_gender); r1.addWidget(self.chart_doswal_perf)
        l.addLayout(r1)

        l.addStretch()
        scroll.setWidget(content)
        layout = QVBoxLayout(self.tab_faculty); layout.setContentsMargins(0,0,0,0); layout.addWidget(scroll)

    def create_chart_container(self, title):
        f = QFrame(); f.setObjectName("content_card"); f.setMinimumHeight(350)
        add_shadow(f)
        vl = QVBoxLayout(f)
        return f
        
    def export_dashboard_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", "Dashboard.pdf", "*.pdf")
        if path:
            current_tab = self.tabs.currentWidget()
            if isinstance(current_tab, QWidget) and current_tab.layout() and current_tab.layout().itemAt(0):
                scroll_area = current_tab.layout().itemAt(0).widget()
                target_widget = scroll_area.widget()
            else:
                return

            scale = 3.0 
            pixmap = QPixmap(target_widget.size() * scale)
            pixmap.fill(Qt.white) 

            p = QPainter(pixmap)
            p.setRenderHint(QPainter.Antialiasing)
            p.setRenderHint(QPainter.TextAntialiasing)
            p.scale(scale, scale)
            
            target_widget.render(p, QPoint(0, 0)) 
            p.end()
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPageOrientation(QPageLayout.Landscape) 
            
            painter = QPainter(printer)
            page_rect = printer.pageRect(QPrinter.DevicePixel)
            
            img_w = pixmap.width()
            img_h = pixmap.height()
            page_w = page_rect.width()
            page_h = page_rect.height()
            
            scale_factor = min(page_w / img_w, page_h / img_h)
            final_w = int(img_w * scale_factor)
            final_h = int(img_h * scale_factor)
            x = int((page_w - final_w) / 2)
            y = int((page_h - final_h) / 2)
            
            painter.drawPixmap(x, y, final_w, final_h, pixmap)
            painter.end()
            
            QMessageBox.information(self, "Sukses", "Halaman Dashboard Aktif berhasil diexport")

    def update_dashboard_stats(self):
        if 'SessionLocal' not in globals() or SessionLocal is None: return
        db = SessionLocal()
        try:
            nm = db.query(Mahasiswa).count()
            nd = db.query(Dosen).count()
            n_prodi = db.query(Mahasiswa.program_studi).distinct().count()
            self.lbl_mhs.setText(str(nm))
            self.lbl_dsn.setText(str(nd))
            self.lbl_prodi.setText(str(n_prodi))

            raw_scores = db.query(Nilai.mahasiswa_id, Nilai.nilai_angka, Matakuliah.sks).join(Matakuliah).all()
            student_gpa = defaultdict(lambda: [0.0, 0]) 
            for mid, val, sks in raw_scores:
                student_gpa[mid][0] += (val * sks)
                student_gpa[mid][1] += sks
            
            critical_count = 0
            final_gpa_map = {} 
            for mid, data in student_gpa.items():
                if data[1] > 0:
                    ipk = data[0] / data[1]
                    final_gpa_map[mid] = ipk
                    if ipk < 2.0: critical_count += 1
            self.lbl_kritis.setText(str(critical_count))

            theme = ThemeColors(self.is_dark).CHART_THEME
            
            series = QLineSeries(); series.setName("Mahasiswa Aktif"); series.setPointsVisible(True); series.setMarkerSize(5.0)
            pen = series.pen(); pen.setWidth(3); pen.setColor(QColor("#3498DB")); series.setPen(pen); series.setColor(QColor("#3498DB"))
            
            scat_trend = QScatterSeries()
            scat_trend.setMarkerSize(1.0)
            scat_trend.setColor(Qt.transparent)
            scat_trend.setPointLabelsVisible(True)
            scat_trend.setPointLabelsFormat("@yPoint")
            if self.is_dark: scat_trend.setPointLabelsColor(QColor("#F1F5F9"))

            trend_data = db.query(Mahasiswa.tahun_masuk, func.count(Mahasiswa.id)).group_by(Mahasiswa.tahun_masuk).order_by(Mahasiswa.tahun_masuk).all()
            min_y, max_y, max_c = 0, 0, 0
            if trend_data:
                years = [y for y, c in trend_data if y is not None]
                counts = [c for y, c in trend_data if y is not None]
                if years:
                    min_y, max_y = min(years), max(years); max_c = max(counts)
                    for y, c in trend_data:
                        if y is not None: 
                            series.append(y, c)
                            scat_trend.append(y, c)
            else: curr_y = datetime.now().year; min_y, max_y = curr_y - 1, curr_y; max_c = 5

            ch = QChart()
            ch.addSeries(series)
            ch.addSeries(scat_trend)
            ch.setTitle("Tren Mahasiswa")
            ch.setTheme(theme); ch.setBackgroundBrush(Qt.NoBrush); ch.legend().setVisible(False)
            if self.is_dark: ch.setTitleBrush(QColor("#F1F5F9"))
            
            axis_x = QValueAxis()
            axis_x.setLabelFormat("%.0f")
            start_x = min_y - 1
            end_x = max_y + 1
            axis_x.setRange(start_x, end_x)
            span_x = end_x - start_x
            axis_x.setTickCount(int(span_x)+1 if span_x < 12 else 6)
            if self.is_dark: axis_x.setLabelsColor(QColor("#F1F5F9"))
            ch.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            scat_trend.attachAxis(axis_x)
            
            axis_y = QValueAxis(); axis_y.setRange(0, max_c + 5); axis_y.setLabelFormat("%.0f")
            if self.is_dark: axis_y.setLabelsColor(QColor("#F1F5F9"))
            ch.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            scat_trend.attachAxis(axis_y)
            
            cv = QChartView(ch); cv.setRenderHint(QPainter.Antialiasing)
            if self.chart_trend.layout().count(): self.chart_trend.layout().itemAt(0).widget().setParent(None)
            self.chart_trend.layout().addWidget(cv)

            gpa_trend_data = defaultdict(list)
            all_mhs = db.query(Mahasiswa).all()
            for m in all_mhs:
                if m.id in final_gpa_map: gpa_trend_data[m.tahun_masuk].append(final_gpa_map[m.id])
            
            series_ipk = QLineSeries(); series_ipk.setPointsVisible(True); series_ipk.setMarkerSize(5); series_ipk.setColor(QColor("#2ECC71"))
            scat_ipk = QScatterSeries(); scat_ipk.setMarkerSize(1.0); scat_ipk.setColor(Qt.transparent); scat_ipk.setPointLabelsVisible(True); scat_ipk.setPointLabelsFormat("@yPoint")
            if self.is_dark: scat_ipk.setPointLabelsColor(QColor("#F1F5F9"))
            
            years_ipk = sorted(gpa_trend_data.keys()); min_yi, max_yi = 0, 0
            if years_ipk:
                min_yi, max_yi = min(years_ipk), max(years_ipk)
                for y in years_ipk:
                    avg = round(sum(gpa_trend_data[y]) / len(gpa_trend_data[y]), 2)
                    series_ipk.append(y, avg); scat_ipk.append(y, avg)
            else: curr = datetime.now().year; min_yi, max_yi = curr-1, curr
            
            ch_ipk = QChart(); ch_ipk.addSeries(series_ipk); ch_ipk.addSeries(scat_ipk); ch_ipk.setTitle("Tren Rata-rata IPK")
            ch_ipk.legend().setVisible(False)
            
            ax_ix = QValueAxis()
            ax_ix.setLabelFormat("%.0f")
            ax_ix.setRange(min_yi - 1, max_yi + 1)
            span_xi = (max_yi + 1) - (min_yi - 1)
            ax_ix.setTickCount(int(span_xi) + 1 if span_xi < 12 else 6)
            
            if self.is_dark: ax_ix.setLabelsColor(QColor("#F1F5F9"))
            ch_ipk.addAxis(ax_ix, Qt.AlignBottom); series_ipk.attachAxis(ax_ix); scat_ipk.attachAxis(ax_ix)
            ax_iy = QValueAxis(); ax_iy.setRange(0, 4.0); ax_iy.setLabelFormat("%.2f")
            if self.is_dark: ax_iy.setLabelsColor(QColor("#F1F5F9"))
            ch_ipk.addAxis(ax_iy, Qt.AlignLeft); series_ipk.attachAxis(ax_iy); scat_ipk.attachAxis(ax_iy)
            ch_ipk.setTheme(theme); ch_ipk.setBackgroundBrush(Qt.NoBrush)
            if self.is_dark: ch_ipk.setTitleBrush(QColor("#F1F5F9"))
            cv_ipk = QChartView(ch_ipk); cv_ipk.setRenderHint(QPainter.Antialiasing)
            if self.chart_ipk_trend.layout().count(): self.chart_ipk_trend.layout().itemAt(0).widget().setParent(None)
            self.chart_ipk_trend.layout().addWidget(cv_ipk)

            series_s = QPieSeries(); series_s.setHoleSize(0.40)
            stat_data = db.query(Mahasiswa.status, func.count(Mahasiswa.id)).group_by(Mahasiswa.status).all()
            col_map = {"Aktif": "#10B981", "Cuti": "#F59E0B", "Lulus": "#3B82F6", "DO": "#EF4444"}
            tot_stat = sum([c for _, c in stat_data])
            for st, cnt in stat_data:
                sl = series_s.append(f"{st}: {cnt}", cnt)
                if st in col_map: sl.setColor(QColor(col_map[st]))
                else: sl.setColor(QColor("#94A3B8"))
                sl.setLabelVisible(True)
                if self.is_dark: sl.setLabelColor(QColor("#F1F5F9"))
            ch_s = QChart(); ch_s.addSeries(series_s); ch_s.setTitle("Distribusi Status")
            ch_s.legend().setVisible(True); ch_s.legend().setAlignment(Qt.AlignRight)
            ch_s.setTheme(theme); ch_s.setBackgroundBrush(Qt.NoBrush)
            if self.is_dark: ch_s.setTitleBrush(QColor("#F1F5F9")); ch_s.legend().setLabelColor(QColor("#F1F5F9"))
            cv_s = QChartView(ch_s); cv_s.setRenderHint(QPainter.Antialiasing)
            if self.chart_status.layout().count(): self.chart_status.layout().itemAt(0).widget().setParent(None)
            self.chart_status.layout().addWidget(cv_s)

            series_d = QBarSeries(); series_d.setLabelsVisible(True); series_d.setLabelsFormat("@value")
            set_d = QBarSet("Mahasiswa"); set_d.setColor(QColor("#9B59B6"))
            buckets = [0, 0, 0, 0] 
            for ipk in final_gpa_map.values():
                if ipk < 2.00: buckets[0] += 1
                elif ipk <= 2.75: buckets[1] += 1
                elif ipk <= 3.50: buckets[2] += 1
                else: buckets[3] += 1
            for b in buckets: set_d.append(b)
            series_d.append(set_d)
            
            ch_d = QChart(); ch_d.addSeries(series_d); ch_d.setTitle("Sebaran IPK")
            
            cats_d = ["&lt; 2.00", "2.00-2.75", "2.76-3.50", "&gt; 3.50"]
            ax_d = QBarCategoryAxis()
            ax_d.append(cats_d)
            if self.is_dark: ax_d.setLabelsColor(QColor("#F1F5F9"))
            ch_d.addAxis(ax_d, Qt.AlignBottom)
            series_d.attachAxis(ax_d)
            
            ay_d = QValueAxis()
            ay_d.setRange(0, max(buckets)+2 if buckets else 5)
            if self.is_dark: ay_d.setLabelsColor(QColor("#F1F5F9"))
            ch_d.addAxis(ay_d, Qt.AlignLeft)
            series_d.attachAxis(ay_d)
            
            ch_d.setTheme(theme); ch_d.setBackgroundBrush(Qt.NoBrush); ch_d.legend().setVisible(False)
            if self.is_dark: ch_d.setTitleBrush(QColor("#F1F5F9"))
            
            cv_d = QChartView(ch_d); cv_d.setRenderHint(QPainter.Antialiasing)
            if self.chart_dist.layout().count(): self.chart_dist.layout().itemAt(0).widget().setParent(None)
            self.chart_dist.layout().addWidget(cv_d)

            fail_data = db.query(Matakuliah.kode_mk, func.count(Nilai.id)).join(Nilai).filter(Nilai.nilai_huruf.in_(['D', 'E'])).group_by(Matakuliah.kode_mk).order_by(func.count(Nilai.id).desc()).limit(5).all()
            series_fail = QBarSeries(); series_fail.setLabelsVisible(True); series_fail.setLabelsFormat("@value")
            set_fail = QBarSet("Jml D/E"); set_fail.setColor(QColor("#E74C3C"))
            cats_fail = []; max_fail = 0
            if fail_data:
                for mk, cnt in fail_data: set_fail.append(cnt); cats_fail.append(mk); max_fail = max(max_fail, cnt)
            else: set_fail.append(0); cats_fail.append("-")
            series_fail.append(set_fail)
            ch_fail = QChart(); ch_fail.addSeries(series_fail); ch_fail.setTitle("MK Nilai Rendah")
            ax_f_x = QBarCategoryAxis(); ax_f_x.append(cats_fail)
            if self.is_dark: ax_f_x.setLabelsColor(QColor("#F1F5F9"))
            ch_fail.addAxis(ax_f_x, Qt.AlignBottom); series_fail.attachAxis(ax_f_x)
            ax_f_y = QValueAxis(); ax_f_y.setRange(0, max_fail+2)
            if self.is_dark: ax_f_y.setLabelsColor(QColor("#F1F5F9"))
            ch_fail.addAxis(ax_f_y, Qt.AlignLeft); series_fail.attachAxis(ax_f_y)
            ch_fail.setTheme(theme); ch_fail.setBackgroundBrush(Qt.NoBrush); ch_fail.legend().setVisible(False)
            if self.is_dark: ch_fail.setTitleBrush(QColor("#F1F5F9"))
            cv_fail = QChartView(ch_fail); cv_fail.setRenderHint(QPainter.Antialiasing)
            if self.chart_mk_fail.layout().count(): self.chart_mk_fail.layout().itemAt(0).widget().setParent(None)
            self.chart_mk_fail.layout().addWidget(cv_fail)

            prodi_gpa_sum = defaultdict(lambda: [0.0, 0])
            for m in all_mhs:
                if m.id in final_gpa_map:
                    prodi_gpa_sum[m.program_studi][0] += final_gpa_map[m.id]
                    prodi_gpa_sum[m.program_studi][1] += 1
            
            series_gp = QBarSeries(); series_gp.setLabelsVisible(True); series_gp.setLabelsFormat("@value")
            set_gp = QBarSet("Rata-rata IPK"); set_gp.setColor(QColor("#1ABC9C"))
            cats_gp = []
            for p, val in prodi_gpa_sum.items():
                avg = round(val[0]/val[1], 2) if val[1] > 0 else 0
                set_gp.append(avg); cats_gp.append(p)
            if not cats_gp: set_gp.append(0); cats_gp.append("-")
            series_gp.append(set_gp)
            ch_gp = QChart(); ch_gp.addSeries(series_gp); ch_gp.setTitle("Rata-rata IPK per Prodi")
            ax_gp_x = QBarCategoryAxis(); ax_gp_x.append(cats_gp)
            if self.is_dark: ax_gp_x.setLabelsColor(QColor("#F1F5F9"))
            ch_gp.addAxis(ax_gp_x, Qt.AlignBottom); series_gp.attachAxis(ax_gp_x)
            ax_gp_y = QValueAxis(); ax_gp_y.setRange(0, 4.0)
            if self.is_dark: ax_gp_y.setLabelsColor(QColor("#F1F5F9"))
            ch_gp.addAxis(ax_gp_y, Qt.AlignLeft); series_gp.attachAxis(ax_gp_y)
            ch_gp.setTheme(theme); ch_gp.setBackgroundBrush(Qt.NoBrush); ch_gp.legend().setVisible(False)
            if self.is_dark: ch_gp.setTitleBrush(QColor("#F1F5F9"))
            cv_gp = QChartView(ch_gp); cv_gp.setRenderHint(QPainter.Antialiasing)
            if self.chart_gpa_prodi_year.layout().count(): self.chart_gpa_prodi_year.layout().itemAt(0).widget().setParent(None)
            self.chart_gpa_prodi_year.layout().addWidget(cv_gp)

            sorted_gpa = sorted(final_gpa_map.items(), key=lambda x: x[1], reverse=True)[:10]
            self.table_top10.setRowCount(0); self.table_top10.setColumnCount(4); self.table_top10.setHorizontalHeaderLabels(["NIM", "Nama", "Prodi", "IPK"])
            self.table_top10.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            for i, (mid, ipk) in enumerate(sorted_gpa):
                m = db.query(Mahasiswa).get(mid)
                if m:
                    self.table_top10.insertRow(i)
                    self.table_top10.setItem(i,0,QTableWidgetItem(m.nim)); self.table_top10.setItem(i,1,QTableWidgetItem(m.nama)); self.table_top10.setItem(i,2,QTableWidgetItem(m.program_studi)); self.table_top10.setItem(i,3,QTableWidgetItem(f"{ipk:.2f}"))

            lowest_gpa = sorted(final_gpa_map.items(), key=lambda x: x[1])[:5]
            self.table_late.setRowCount(0); self.table_late.setColumnCount(4); self.table_late.setHorizontalHeaderLabels(["NIM", "Nama", "Prodi", "IPK"])
            self.table_late.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            for i, (mid, ipk) in enumerate(lowest_gpa):
                m = db.query(Mahasiswa).get(mid)
                if m:
                    self.table_late.insertRow(i)
                    self.table_late.setItem(i,0,QTableWidgetItem(m.nim))
                    self.table_late.setItem(i,1,QTableWidgetItem(m.nama))
                    self.table_late.setItem(i,2,QTableWidgetItem(m.program_studi))
                    self.table_late.setItem(i,3,QTableWidgetItem(f"{ipk:.2f}"))

            gen_data = db.query(Mahasiswa.program_studi, Mahasiswa.gender, func.count(Mahasiswa.id)).group_by(Mahasiswa.program_studi, Mahasiswa.gender).all()
            data_map = defaultdict(lambda: {'L': 0, 'P': 0}); cats_g = set()
            for p, g, c in gen_data:
                if p: data_map[p][g] = c; cats_g.add(p)
            sorted_cats_g = sorted(list(cats_g)) if cats_g else ["-"]
            set_gl = QBarSet("Laki-laki"); set_gl.setColor(QColor("#3498DB"))
            set_gp = QBarSet("Perempuan"); set_gp.setColor(QColor("#E91E63"))
            for c in sorted_cats_g: set_gl.append(data_map[c]['L']); set_gp.append(data_map[c]['P'])
            series_gen = QStackedBarSeries()
            series_gen.setLabelsVisible(True); series_gen.setLabelsFormat("@value"); series_gen.setLabelsPosition(QBarSeries.LabelsCenter)
            series_gen.append(set_gl); series_gen.append(set_gp)
            ch_gen = QChart(); ch_gen.addSeries(series_gen); ch_gen.setTitle("Demografi Gender")
            ax_gx = QBarCategoryAxis(); ax_gx.append(sorted_cats_g)
            if self.is_dark: ax_gx.setLabelsColor(QColor("#F1F5F9"))
            ch_gen.addAxis(ax_gx, Qt.AlignBottom); series_gen.attachAxis(ax_gx)
            ax_gy = QValueAxis(); ax_gy.setLabelFormat("%.0f")
            if self.is_dark: ax_gy.setLabelsColor(QColor("#F1F5F9"))
            ch_gen.addAxis(ax_gy, Qt.AlignLeft); series_gen.attachAxis(ax_gy)
            ch_gen.setTheme(theme); ch_gen.setBackgroundBrush(Qt.NoBrush)
            if self.is_dark: ch_gen.setTitleBrush(QColor("#F1F5F9")); ch_gen.legend().setLabelColor(QColor("#F1F5F9"))
            cv_gen = QChartView(ch_gen); cv_gen.setRenderHint(QPainter.Antialiasing)
            if self.chart_gender.layout().count(): self.chart_gender.layout().itemAt(0).widget().setParent(None)
            self.chart_gender.layout().addWidget(cv_gen)

            doswal_perf = defaultdict(list)
            for m in all_mhs:
                if m.dosen_wali_id and m.id in final_gpa_map:
                    doswal_perf[m.dosen_wali_id].append(final_gpa_map[m.id])
            doswal_avg = []
            for did, gpas in doswal_perf.items():
                d = db.query(Dosen).get(did)
                if d: doswal_avg.append((d.nama, sum(gpas)/len(gpas)))
            doswal_avg.sort(key=lambda x: x[1], reverse=True)
            top_doswal = doswal_avg[:5]
            
            series_dp = QHorizontalBarSeries(); series_dp.setLabelsVisible(True); series_dp.setLabelsFormat("@value")
            set_dp = QBarSet("Rata-rata IPK Binaan"); set_dp.setColor(QColor("#F39C12"))
            cats_dp = []
            for name, avg in top_doswal:
                set_dp.append(round(avg, 2)); cats_dp.append(name.split(',')[0][:15]) 
            if not cats_dp: set_dp.append(0); cats_dp.append("-")
            series_dp.append(set_dp)
            
            ch_dp = QChart(); ch_dp.addSeries(series_dp); ch_dp.setTitle("Top Kinerja Dosen Wali")
            ax_dpx = QBarCategoryAxis(); ax_dpx.append(cats_dp)
            if self.is_dark: ax_dpx.setLabelsColor(QColor("#F1F5F9"))
            ch_dp.addAxis(ax_dpx, Qt.AlignLeft); series_dp.attachAxis(ax_dpx)
            ax_dpy = QValueAxis(); ax_dpy.setRange(0, 4.0)
            if self.is_dark: ax_dpy.setLabelsColor(QColor("#F1F5F9"))
            ch_dp.addAxis(ax_dpy, Qt.AlignBottom); series_dp.attachAxis(ax_dpy)
            
            ch_dp.setTheme(theme); ch_dp.setBackgroundBrush(Qt.NoBrush); ch_dp.legend().setVisible(False)
            if self.is_dark: ch_dp.setTitleBrush(QColor("#F1F5F9"))
            cv_dp = QChartView(ch_dp); cv_dp.setRenderHint(QPainter.Antialiasing)
            if self.chart_doswal_perf.layout().count(): self.chart_doswal_perf.layout().itemAt(0).widget().setParent(None)
            self.chart_doswal_perf.layout().addWidget(cv_dp)

        finally: db.close()

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Informasi Akademik Pro")
        self.resize(1280, 800)
        
        self.is_dark = is_system_dark_mode()
        self.setStyleSheet(get_stylesheet(self.is_dark))
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.login = LoginWidget(self.is_dark)
        self.login.login_success_signal.connect(self.on_login)
        self.stack.addWidget(self.login)

    def on_login(self, user, role):
        if self.stack.count() > 1:
            old_widget = self.stack.widget(1)
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()

        self.main = MainWidget(user, role, self.is_dark)
        self.main.logout_signal.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.main)
        self.stack.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    
    win = AppWindow()
    win.showMaximized()
    sys.exit(app.exec())