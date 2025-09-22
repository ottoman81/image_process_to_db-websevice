import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QLineEdit, QGroupBox, QComboBox, 
                             QSpinBox, QCheckBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from Domain.Models import CameraConfig, OCRConfig, ProcessingParams

class CameraTab(QWidget):
    def __init__(self, camera_service, ocr_service):
        super().__init__()
        self.camera_service = camera_service
        self.ocr_service = ocr_service
        self.camera_config = CameraConfig()
        self.ocr_config = OCRConfig()
        self.ocr_config.selection_rect = QRect(100, 100, 200, 150)
        self.processing_params = ProcessingParams()
        
        self.is_selecting = False
        self.is_dragging = False
        self.selection_start = None
        self.original_selection = None
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Camera view
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 2px solid black; background-color: #f0f0f0;")
        self.camera_label.mousePressEvent = self.mouse_press_event
        self.camera_label.mouseMoveEvent = self.mouse_move_event
        self.camera_label.mouseReleaseEvent = self.mouse_release_event
        
        # Processed image
        self.processed_label = QLabel()
        self.processed_label.setMinimumSize(320, 240)
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet("border: 2px solid blue; background-color: #f0f0f0;")
        
        # Image layout
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.camera_label)
        image_layout.addWidget(self.processed_label)
        
        layout.addLayout(image_layout)
        
        # Controls
        control_layout = QHBoxLayout()
        
        # Camera settings
        cam_group = QGroupBox("Kamera Ayarları")
        cam_layout = QVBoxLayout()
        
        self.cam_combo = QComboBox()
        self.refresh_cam_list()
        cam_layout.addWidget(QLabel("Kamera:"))
        cam_layout.addWidget(self.cam_combo)
        
        # RTSP connection settings
        rtsp_group = QGroupBox("RTSP Bağlantı Ayarları")
        rtsp_layout = QFormLayout()
        
        self.rtsp_url_input = QLineEdit()
        self.rtsp_url_input.setPlaceholderText("rtsp://192.168.1.100:554/stream")
        rtsp_layout.addRow("RTSP URL:", self.rtsp_url_input)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        rtsp_layout.addRow("Kullanıcı Adı:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("password")
        self.password_input.setEchoMode(QLineEdit.Password)
        rtsp_layout.addRow("Şifre:", self.password_input)
        
        self.use_rtsp_checkbox = QCheckBox("RTSP Kullan")
        rtsp_layout.addRow(self.use_rtsp_checkbox)
        
        rtsp_group.setLayout(rtsp_layout)
        cam_layout.addWidget(rtsp_group)
        
        self.btn_start = QPushButton("📷 Başlat")
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_start.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        cam_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹️ Durdur")
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_stop.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        cam_layout.addWidget(self.btn_stop)
        
        self.btn_refresh = QPushButton("🔄 Yenile")
        self.btn_refresh.clicked.connect(self.refresh_cam_list)
        cam_layout.addWidget(self.btn_refresh)
        
        cam_group.setLayout(cam_layout)
        
        # OCR settings
        ocr_group = QGroupBox("OCR Ayarları")
        ocr_layout = QVBoxLayout()
        
        self.btn_ocr = QPushButton("🔍 OCR Çalıştır")
        self.btn_ocr.clicked.connect(self.run_ocr)
        self.btn_ocr.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        ocr_layout.addWidget(self.btn_ocr)
        
        # Language selection
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["tur", "eng", "tur+eng", "osd"])
        ocr_layout.addWidget(QLabel("OCR Dili:"))
        ocr_layout.addWidget(self.lang_combo)
        
        # Selection size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Genişlik:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(10, 1000)
        self.spin_width.setValue(200)
        size_layout.addWidget(self.spin_width)
        
        size_layout.addWidget(QLabel("Yükseklik:"))
        self.spin_height = QSpinBox()
        self.spin_height.setRange(10, 1000)
        self.spin_height.setValue(150)
        size_layout.addWidget(self.spin_height)
        
        self.btn_set_size = QPushButton("📏 Boyutu Ayarla")
        self.btn_set_size.clicked.connect(self.set_selection_size)
        size_layout.addWidget(self.btn_set_size)
        
        ocr_layout.addLayout(size_layout)
        ocr_group.setLayout(ocr_layout)
        
        control_layout.addWidget(cam_group)
        control_layout.addWidget(ocr_group)
        
        layout.addLayout(control_layout)
        
        # OCR results
        result_group = QGroupBox("📄 OCR Sonuçları")
        result_layout = QVBoxLayout()
        
        self.text_result = QTextEdit()
        self.text_result.setMaximumHeight(120)
        self.text_result.setStyleSheet("font-family: Consolas; font-size: 11pt;")
        result_layout.addWidget(self.text_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        self.setLayout(layout)
        
        # Timer for camera update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def connect_signals(self):
        self.camera_service.frame_updated.connect(self.display_frame)
        self.camera_service.camera_error.connect(self.handle_camera_error)
        
    def refresh_cam_list(self):
        self.cam_combo.clear()
        cameras = self.camera_service.get_available_cameras()
        for cam in cameras:
            self.cam_combo.addItem(cam)
        self.cam_combo.addItem("RTSP Bağlantısı")
            
    def start_camera(self):
        self.camera_config.index = self.cam_combo.currentIndex()
        self.camera_config.rtsp_url = self.rtsp_url_input.text()
        self.camera_config.username = self.username_input.text()
        self.camera_config.password = self.password_input.text()
        self.camera_config.use_rtsp = self.use_rtsp_checkbox.isChecked()
        
        if self.camera_service.start_camera(self.camera_config):
            self.timer.start(30)
            
    def stop_camera(self):
        self.timer.stop()
        self.camera_service.stop_camera()
        self.camera_label.clear()
        self.processed_label.clear()
        self.text_result.setText("Kamera durduruldu.")
        
    def update_frame(self):
        frame = self.camera_service.read_frame()
        if frame is not None:
            self.update_processed_frame()
                
    def display_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Draw selection rectangle
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(255, 0, 0), 3, Qt.DashLine))
        painter.drawRect(self.ocr_config.selection_rect)
        
        # Corner handles
        handle_size = 6
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.white)
        
        points = [
            self.ocr_config.selection_rect.topLeft(),
            self.ocr_config.selection_rect.topRight(),
            self.ocr_config.selection_rect.bottomRight(),
            self.ocr_config.selection_rect.bottomLeft()
        ]
        
        for point in points:
            painter.drawRect(point.x() - handle_size//2, point.y() - handle_size//2, 
                           handle_size, handle_size)
        
        # Size info
        painter.setPen(QPen(Qt.yellow))
        painter.setFont(QFont("Arial", 10))
        info = f"{self.ocr_config.selection_rect.width()}×{self.ocr_config.selection_rect.height()}"
        painter.drawText(self.ocr_config.selection_rect.x(), self.ocr_config.selection_rect.y() - 10, info)
        
        painter.end()
        
        self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), 
                                                Qt.KeepAspectRatio, 
                                                Qt.SmoothTransformation))
    
    def update_processed_frame(self):
        frame = self.camera_service.get_frame()
        if frame is None or self.ocr_config.selection_rect.isEmpty():
            return
            
        x, y, w, h = (self.ocr_config.selection_rect.x(), self.ocr_config.selection_rect.y(),
                      self.ocr_config.selection_rect.width(), self.ocr_config.selection_rect.height())
        
        cropped = frame[y:y+h, x:x+w]
        processed = self.ocr_service.preprocess_image(cropped, self.processing_params)
        
        # Convert to QImage
        if isinstance(processed, np.ndarray):
            if len(processed.shape) == 2:  # Grayscale
                h, w = processed.shape
                bytes_per_line = w
                qt_image = QImage(processed.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
            else:  # Color
                h, w, ch = processed.shape
                bytes_per_line = ch * w
                qt_image = QImage(processed.data, w, h, bytes_per_line, QImage.Format_RGB888)
        else:  # PIL Image
            qt_image = QImage(processed.tobytes(), processed.width, processed.height, 
                            processed.width, QImage.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(qt_image)
        self.processed_label.setPixmap(pixmap.scaled(self.processed_label.size(), 
                                                   Qt.KeepAspectRatio, 
                                                   Qt.SmoothTransformation))
        
    def handle_camera_error(self, error_msg):
        self.text_result.setText(error_msg)
        
    def mouse_press_event(self, event):
        pos = event.pos()
        scaled_pos = self.scale_position(pos)
        
        if event.button() == Qt.LeftButton:
            if self.ocr_config.selection_rect.contains(scaled_pos):
                self.is_dragging = True
                self.original_selection = QRect(self.ocr_config.selection_rect)
                self.drag_start = scaled_pos
            else:
                self.is_selecting = True
                self.selection_start = scaled_pos
                self.ocr_config.selection_rect = QRect(scaled_pos, scaled_pos)
                
        elif event.button() == Qt.RightButton:
            self.ocr_config.selection_rect = QRect()
            
    def mouse_move_event(self, event):
        pos = event.pos()
        scaled_pos = self.scale_position(pos)
        
        if self.is_selecting:
            x = min(self.selection_start.x(), scaled_pos.x())
            y = min(self.selection_start.y(), scaled_pos.y())
            width = abs(self.selection_start.x() - scaled_pos.x())
            height = abs(self.selection_start.y() - scaled_pos.y())
            self.ocr_config.selection_rect = QRect(x, y, width, height)
            
        elif self.is_dragging:
            delta_x = scaled_pos.x() - self.drag_start.x()
            delta_y = scaled_pos.y() - self.drag_start.y()
            
            new_rect = QRect(self.original_selection)
            new_rect.translate(delta_x, delta_y)
            
            frame = self.camera_service.get_frame()
            if frame is not None:
                if new_rect.x() < 0: new_rect.moveLeft(0)
                if new_rect.y() < 0: new_rect.moveTop(0)
                if new_rect.right() > frame.shape[1]: new_rect.moveRight(frame.shape[1])
                if new_rect.bottom() > frame.shape[0]: new_rect.moveBottom(frame.shape[0])
                    
            self.ocr_config.selection_rect = new_rect
            
    def mouse_release_event(self, event):
        self.is_selecting = False
        self.is_dragging = False
        
    def scale_position(self, pos):
        frame = self.camera_service.get_frame()
        if frame is None:
            return pos
            
        label_size = self.camera_label.size()
        frame_size = (frame.shape[1], frame.shape[0])
        
        scale_x = frame_size[0] / label_size.width()
        scale_y = frame_size[1] / label_size.height()
        
        return pos * max(scale_x, scale_y)
        
    def set_selection_size(self):
        width = self.spin_width.value()
        height = self.spin_height.value()
        
        center_x = self.ocr_config.selection_rect.x() + self.ocr_config.selection_rect.width() // 2
        center_y = self.ocr_config.selection_rect.y() + self.ocr_config.selection_rect.height() // 2
        
        new_rect = QRect(center_x - width//2, center_y - height//2, width, height)
        
        frame = self.camera_service.get_frame()
        if frame is not None:
            if new_rect.x() < 0: new_rect.moveLeft(0)
            if new_rect.y() < 0: new_rect.moveTop(0)
            if new_rect.right() > frame.shape[1]: new_rect.moveRight(frame.shape[1])
            if new_rect.bottom() > frame.shape[0]: new_rect.moveBottom(frame.shape[0])
                
        self.ocr_config.selection_rect = new_rect
        
    def run_ocr(self):
        if self.camera_service.get_frame() is None or self.ocr_config.selection_rect.isEmpty():
            self.text_result.setText("Lütfen önce bir alan seçin!")
            return
            
        x, y, w, h = (self.ocr_config.selection_rect.x(), self.ocr_config.selection_rect.y(),
                      self.ocr_config.selection_rect.width(), self.ocr_config.selection_rect.height())
        
        cropped = self.camera_service.get_frame()[y:y+h, x:x+w]
        processed = self.ocr_service.preprocess_image(cropped, self.processing_params)
        
        try:
            lang = self.lang_combo.currentText()
            text = self.ocr_service.extract_text(processed, lang)
            self.text_result.setText(text.strip() if text.strip() else "Metin bulunamadı")
        except Exception as e:
            self.text_result.setText(f"OCR hatası: {str(e)}")
    
    def get_processing_params(self):
        """Processing parametrelerini döndür"""

        return self.processing_params
