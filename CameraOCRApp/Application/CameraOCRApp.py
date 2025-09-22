# Application/CameraOCRApp.py
import sys
from PyQt5.QtWidgets import QApplication
from UI.MainWindow import MainWindow  # Burası düzeltildi
from Infrastructure.CameraService import CameraService
from Infrastructure.OCRService import OCRService
from Infrastructure.DatabaseService import DatabaseService
from Infrastructure.WebService import WebService

class CameraOCRApp:
    def __init__(self, argv):
        self.app = QApplication(argv)
        self.camera_service = CameraService()
        self.ocr_service = OCRService()
        self.database_service = DatabaseService()
        self.web_service = WebService()
        
        self.main_window = MainWindow(
            self.camera_service, 
            self.ocr_service, 
            self.database_service, 
            self.web_service
        )
        
    def run(self):
        self.main_window.show()
        return self.app.exec_()