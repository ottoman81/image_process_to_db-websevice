import pyodbc
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QCheckBox, QPushButton, 
                             QLabel, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QComboBox, QDateTimeEdit, QRadioButton)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont
from Domain.Models import DatabaseConfig, SensorData, OCRSensorData
from datetime import datetime

class DatabaseTab(QWidget):
    def __init__(self, database_service, camera_service, ocr_service, ocr_config, web_service):
        super().__init__()
        self.database_service = database_service
        self.camera_service = camera_service
        self.ocr_service = ocr_service
        self.ocr_config = ocr_config
        self.web_service = web_service
        self.config = DatabaseConfig()
        
        # Sabit bağlantı bilgileri buraya eklendi
        self.config.server = "server"
        self.config.database = "db"
        self.config.use_windows_auth = False
        self.config.username = "sa"
        self.config.password = "pass"
        self.config.port = 1433

        self.processing_params = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_ocr_and_save)
        self.ocr_timer = QTimer()
        self.ocr_timer.timeout.connect(self.read_ocr_temperature)
        
        self.init_ui()
        self.connect_db()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Veri Kayıt Seçeneği Grubu
        data_target_group = QGroupBox("Veri Kayıt Seçeneği")
        data_target_layout = QVBoxLayout()
        
        self.db_radio = QRadioButton("Veritabanına Kaydet")
        self.db_radio.setChecked(True)
        self.db_radio.toggled.connect(self.toggle_web_service_input)
        
        self.web_service_radio = QRadioButton("Web Servisine Gönder")
        self.web_service_radio.toggled.connect(self.toggle_web_service_input)
        
        self.web_service_url_input = QLineEdit("webservice")
        self.web_service_url_input.setPlaceholderText("Web Servis URL'sini girin (örn: http://localhost:5000/api/data)")
        self.web_service_url_input.hide()
        
        data_target_layout.addWidget(self.db_radio)
        data_target_layout.addWidget(self.web_service_radio)
        data_target_layout.addWidget(self.web_service_url_input)
        data_target_group.setLayout(data_target_layout)
        
        # Veritabanı Bağlantı Ayarları
        connection_group = QGroupBox("📊 Veritabanı Bağlantı Ayarları")
        connection_layout = QFormLayout()
        
        self.server_input = QLineEdit()
        self.port_spin = QSpinBox()
        self.database_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.windows_auth_check = QCheckBox("Windows Kimlik Doğrulaması Kullan")
        
        # Sabit değerleri göster
        self.server_input.setText(self.config.server)
        self.port_spin.setValue(self.config.port)
        self.database_input.setText(self.config.database)
        self.windows_auth_check.setChecked(self.config.use_windows_auth)
        self.toggle_auth_fields()
        
        self.server_input.setReadOnly(True)
        self.port_spin.setReadOnly(True)
        self.database_input.setReadOnly(True)
        self.user_input.setReadOnly(True)
        self.password_input.setReadOnly(True)
        self.windows_auth_check.setEnabled(False)
        
        connection_layout.addRow("Sunucu:", self.server_input)
        connection_layout.addRow("Port:", self.port_spin)
        connection_layout.addRow("Veritabanı:", self.database_input)
        connection_layout.addRow("Kullanıcı Adı:", self.user_input)
        connection_layout.addRow("Şifre:", self.password_input)
        connection_layout.addRow("", self.windows_auth_check)

        conn_buttons_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Bağlan")
        self.test_conn_btn = QPushButton("Bağlantıyı Test Et")
        self.disconnect_btn = QPushButton("Bağlantıyı Kes")
        conn_buttons_layout.addWidget(self.connect_btn)
        conn_buttons_layout.addWidget(self.test_conn_btn)
        conn_buttons_layout.addWidget(self.disconnect_btn)
        self.connect_btn.hide()
        self.disconnect_btn.hide()
        self.test_conn_btn.hide()
        
        connection_layout.addRow(conn_buttons_layout)
        connection_group.setLayout(connection_layout)
        
        ocr_group = QGroupBox("OCR Veri Okuma Ayarları")
        ocr_layout = QFormLayout()
        
        self.ocr_auto_check = QCheckBox("Otomatik OCR Okuma")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 600)
        self.interval_spin.setValue(10)
        self.interval_spin.setSuffix(" saniye")
        
        self.ocr_start_btn = QPushButton("Otomatik Okumayı Başlat")
        self.ocr_stop_btn = QPushButton("Otomatik Okumayı Durdur")
        self.ocr_test_btn = QPushButton("Manuel OCR Testi")
        self.ocr_stop_btn.setEnabled(False)
        
        ocr_layout.addRow("Otomatik Okuma:", self.ocr_auto_check)
        ocr_layout.addRow("Okuma Aralığı:", self.interval_spin)
        
        ocr_buttons_layout = QHBoxLayout()
        ocr_buttons_layout.addWidget(self.ocr_test_btn)
        ocr_buttons_layout.addWidget(self.ocr_start_btn)
        ocr_buttons_layout.addWidget(self.ocr_stop_btn)
        
        ocr_layout.addRow(ocr_buttons_layout)
        ocr_group.setLayout(ocr_layout)
        
        # Veri Tablosu
        table_group = QGroupBox("Son Okunan Veriler")
        table_layout = QVBoxLayout()
        
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Sıcaklık", "Nem", "Zaman Damgası"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.refresh_btn = QPushButton("Verileri Yenile")
        
        table_layout.addWidget(self.table_widget)
        table_layout.addWidget(self.refresh_btn)
        table_group.setLayout(table_layout)
        
        # Log
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        self.log_text.setStyleSheet("background-color: #f0f0f0; border: 1px solid #d0d0d0;")
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        layout.addWidget(data_target_group)
        layout.addWidget(connection_group)
        layout.addWidget(ocr_group)
        layout.addWidget(table_group)
        layout.addWidget(log_group)
        
        self.setLayout(layout)
        
        # Sinyal bağlantıları
        self.connect_btn.clicked.connect(self.connect_db)
        self.test_conn_btn.clicked.connect(self.test_db_connection)
        self.disconnect_btn.clicked.connect(self.disconnect_db)
        self.windows_auth_check.stateChanged.connect(self.toggle_auth_fields)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # OCR Sinyalleri
        self.ocr_start_btn.clicked.connect(self.start_ocr_reading)
        self.ocr_stop_btn.clicked.connect(self.stop_ocr_reading)
        self.ocr_test_btn.clicked.connect(self.test_ocr_reading)
        
    def toggle_web_service_input(self):
        is_web_service_selected = self.web_service_radio.isChecked()
        self.web_service_url_input.setVisible(is_web_service_selected)
        self.connect_btn.setEnabled(not is_web_service_selected)
        self.test_conn_btn.setEnabled(not is_web_service_selected)
        self.disconnect_btn.setEnabled(not is_web_service_selected)
        self.log_text.append(f"[Ayarlar] Veri hedefi {'Web Servis' if is_web_service_selected else 'Veritabanı'} olarak ayarlandı.")

    def set_processing_params(self, params):
        self.processing_params = params

    def connect_db(self):
        success, message = self.database_service.connect(self.config)
        self.show_message(message, "Bağlantı Başarılı" if success else "Bağlantı Hatası")
        if success:
            self.log_text.append("[DB] Bağlantı başarılı.")
            self.refresh_data()
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
        else:
            self.log_text.append(f"[DB] Bağlantı hatası: {message}")
            self.show_message("Lütfen bağlantı bilgilerini kontrol edin veya SQL Server'ın çalıştığından emin olun.", "Bağlantı Hatası")

    def disconnect_db(self):
        self.database_service.disconnect()
        self.show_message("Veritabanı bağlantısı kesildi.", "Bağlantı Kesildi")
        self.log_text.append("[DB] Bağlantı kesildi.")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)

    def test_db_connection(self):
        success, message = self.database_service.test_connection(self.config)
        self.show_message(message, "Bağlantı Testi Başarılı" if success else "Bağlantı Testi Başarısız")
        
    def toggle_auth_fields(self):
        is_checked = self.windows_auth_check.isChecked()
        self.user_input.setEnabled(not is_checked)
        self.password_input.setEnabled(not is_checked)

    def read_ocr_temperature(self):
        frame = self.camera_service.get_frame()
        
        if frame is None:
            self.log_text.append("[OCR] Hata: Kamera aktif değil!")
            return

        x = self.ocr_config.selection_rect.x()
        y = self.ocr_config.selection_rect.y()
        w = self.ocr_config.selection_rect.width()
        h = self.ocr_config.selection_rect.height()
        
        if w == 0 or h == 0:
            self.log_text.append("[OCR] Hata: Lütfen Kamera sekmesinden bir OCR alanı seçin!")
            return
            
        try:
            cropped_frame = frame[y:y+h, x:x+w]
            processed_image = self.ocr_service.preprocess_image(cropped_frame, self.processing_params)
            text = self.ocr_service.extract_text(processed_image, self.ocr_config.language)
            self.log_text.append(f"[OCR] Okunan Ham Veri: {text.strip()}")
            
            ocr_sensor_data = self.ocr_service.parse_sensor_data(text)
            
            if ocr_sensor_data:
                full_sensor_data = SensorData(
                    temperature=ocr_sensor_data.temperature,
                    humidity=70.0,
                    timestamp=datetime.now()
                )
                
                # Yeni filtreleme mantığı buraya eklendi
                if 0 <= full_sensor_data.temperature <= 50:
                    self.log_text.append(f"ⓘ Veri filtrelendi: Sıcaklık {full_sensor_data.temperature}°C. 0-50°C aralığındaki veriler kaydedilmiyor.")
                    return
                
                # Seçilen hedefe göre veriyi kaydet veya gönder
                if self.db_radio.isChecked():
                    if not self.database_service.is_connected():
                         self.log_text.append("[DB] Hata: Veritabanı bağlantısı bulunamadı.")
                         return
                    success, message = self.database_service.insert_sensor_data(full_sensor_data)
                    log_prefix = "[DB]"
                elif self.web_service_radio.isChecked():
                    url = self.web_service_url_input.text().strip()
                    success, message = self.web_service.send_sensor_data(full_sensor_data, url)
                    log_prefix = "[Web Servis]"
                else:
                    self.log_text.append("✗ Hata: Veri kayıt hedefi seçilmedi!")
                    return

                if success:
                    self.log_text.append(f"✓ {log_prefix} Başarılı: {message}")
                else:
                    self.log_text.append(f"✗ {log_prefix} Hata: {message}")
            else:
                self.log_text.append("✗ Hata: Metinden geçerli sıcaklık verisi çıkarılamadı!")
                
            self.refresh_data()
            
        except Exception as e:
            self.log_text.append(f"Bir hata oluştu: {str(e)}")

    def start_ocr_reading(self):
        if self.db_radio.isChecked() and not self.database_service.is_connected():
            self.log_text.append("Lütfen önce veritabanına bağlanın!")
            return
        
        if self.web_service_radio.isChecked() and not self.web_service_url_input.text().strip():
             self.log_text.append("Lütfen Web Servis URL'sini girin!")
             return

        interval = self.interval_spin.value() * 1000
        self.ocr_timer.start(interval)
        
        self.ocr_start_btn.setEnabled(False)
        self.ocr_stop_btn.setEnabled(True)
        self.log_text.append(f"[OCR] Otomatik okuma başlatıldı ({interval//1000}s aralıklarla)")
    
    def stop_ocr_reading(self):
        self.ocr_timer.stop()
        self.ocr_start_btn.setEnabled(True)
        self.ocr_stop_btn.setEnabled(False)
        self.log_text.append("[OCR] Otomatik okuma durduruldu")
    
    def test_ocr_reading(self):
        self.read_ocr_temperature()
    
    def auto_ocr_and_save(self):
        if self.ocr_auto_check.isChecked():
            self.read_ocr_temperature()
    
    def refresh_data(self):
        if not self.database_service.is_connected():
            return
        
        data = self.database_service.get_last_n_records(20)
        
        self.table_widget.setRowCount(len(data))
        
        for row, sensor_data in enumerate(data):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(sensor_data.id)))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(sensor_data.temperature)))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(sensor_data.humidity)))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(sensor_data.timestamp)))

    def show_message(self, message, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()