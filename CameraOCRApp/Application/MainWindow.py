from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from UI.CameraTab import CameraTab
from UI.ProcessingTab import ProcessingTab
from UI.DatabaseTab import DatabaseTab

class MainWindow(QMainWindow):
    def __init__(self, camera_service, ocr_service, database_service):
        super().__init__()
        self.camera_service = camera_service
        self.ocr_service = ocr_service
        self.database_service = database_service
        
        self.setWindowTitle("Gelişmiş Kamera OCR ve Sıcaklık Veritabanı Uygulaması")
        self.setGeometry(100, 100, 1600, 1000)
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Tab widget for different sections
        tab_widget = QTabWidget()
        
        # Create tabs
        self.camera_tab = CameraTab(self.camera_service, self.ocr_service)
        self.processing_tab = ProcessingTab(self.camera_service)
        
        # DatabaseTab'ı oluştururken camera_tab'in ocr_config'ini parametre olarak veriyoruz
        self.database_tab = DatabaseTab(self.database_service, self.camera_service, self.ocr_service, self.camera_tab.ocr_config)
        
        # Processing parametrelerini paylaş
        self.database_tab.set_processing_params(self.camera_tab.get_processing_params())
        
        # Add tabs
        tab_widget.addTab(self.camera_tab, "📷 Kamera & OCR")
        tab_widget.addTab(self.processing_tab, "🎨 Görüntü İşleme")
        tab_widget.addTab(self.database_tab, "📊 Sıcaklık Veritabanı")
        
        main_layout.addWidget(tab_widget)
        central_widget.setLayout(main_layout)