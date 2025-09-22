from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
                             QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, 
                             QPushButton, QScrollArea)
from PyQt5.QtCore import Qt
from Domain.Models import ProcessingParams

class ProcessingTab(QWidget):
    def __init__(self, camera_service):
        super().__init__()
        self.camera_service = camera_service
        self.processing_params = ProcessingParams()
        self.init_ui()
        
    def init_ui(self):
        # Ana layout
        main_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Görüntü işleme kontrolleri
        processing_group = QGroupBox("🎨 Görüntü İşleme Ayarları")
        processing_form = QFormLayout()
        
        # Kontrast
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(1, 400)
        self.contrast_slider.setValue(200)
        self.contrast_slider.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Kontrast:", self.contrast_slider)
        
        # Parlaklık
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(1, 300)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Parlaklık:", self.brightness_slider)
        
        # Keskinlik
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setRange(1, 300)
        self.sharpness_slider.setValue(100)
        self.sharpness_slider.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Keskinlik:", self.sharpness_slider)
        
        # Eşik değeri
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 255)
        self.threshold_spin.setValue(128)
        self.threshold_spin.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Eşik Değeri:", self.threshold_spin)
        
        # Gamma
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.1, 5.0)
        self.gamma_spin.setSingleStep(0.1)
        self.gamma_spin.setValue(1.0)
        self.gamma_spin.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Gamma:", self.gamma_spin)
        
        # Bulanıklık
        self.blur_spin = QSpinBox()
        self.blur_spin.setRange(0, 10)
        self.blur_spin.setValue(0)
        self.blur_spin.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Bulanıklık:", self.blur_spin)
        
        # Genişletme
        self.dilate_spin = QSpinBox()
        self.dilate_spin.setRange(1, 5)
        self.dilate_spin.setValue(1)
        self.dilate_spin.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Genişletme:", self.dilate_spin)
        
        # Aşındırma
        self.erode_spin = QSpinBox()
        self.erode_spin.setRange(1, 5)
        self.erode_spin.setValue(1)
        self.erode_spin.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Aşındırma:", self.erode_spin)
        
        # Gürültü azaltma
        self.denoise_spin = QSpinBox()
        self.denoise_spin.setRange(0, 20)
        self.denoise_spin.setValue(0)
        self.denoise_spin.valueChanged.connect(self.update_processing_params)
        processing_form.addRow("Gürültü Azaltma:", self.denoise_spin)
        
        # Checkbox'lar
        self.adaptive_check = QCheckBox("Adaptif Eşikleme")
        self.adaptive_check.stateChanged.connect(self.update_processing_params)
        processing_form.addRow(self.adaptive_check)
        
        self.invert_check = QCheckBox("Renkleri Ters Çevir")
        self.invert_check.stateChanged.connect(self.update_processing_params)
        processing_form.addRow(self.invert_check)
        
        # Reset butonu
        self.btn_reset = QPushButton("🔄 Varsayılanlara Sıfırla")
        self.btn_reset.clicked.connect(self.reset_processing_params)
        processing_form.addRow(self.btn_reset)
        
        processing_group.setLayout(processing_form)
        scroll_layout.addWidget(processing_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        # Ana layout'a scroll area'yı ekle
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def update_processing_params(self):
        self.processing_params.contrast = self.contrast_slider.value() / 100.0
        self.processing_params.brightness = self.brightness_slider.value() / 100.0
        self.processing_params.sharpness = self.sharpness_slider.value() / 100.0
        self.processing_params.threshold = self.threshold_spin.value()
        self.processing_params.blur = self.blur_spin.value()
        self.processing_params.dilate = self.dilate_spin.value()
        self.processing_params.erode = self.erode_spin.value()
        self.processing_params.gamma = self.gamma_spin.value()
        self.processing_params.denoise = self.denoise_spin.value()
        self.processing_params.adaptive_thresh = self.adaptive_check.isChecked()
        self.processing_params.invert = self.invert_check.isChecked()
        
    def reset_processing_params(self):
        self.contrast_slider.setValue(200)
        self.brightness_slider.setValue(100)
        self.sharpness_slider.setValue(100)
        self.threshold_spin.setValue(128)
        self.blur_spin.setValue(0)
        self.dilate_spin.setValue(1)
        self.erode_spin.setValue(1)
        self.gamma_spin.setValue(1.0)
        self.denoise_spin.setValue(0)
        self.adaptive_check.setChecked(False)
        self.invert_check.setChecked(False)
        self.update_processing_params()