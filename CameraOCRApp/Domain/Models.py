from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from PyQt5.QtCore import QRect
from datetime import datetime
import re

@dataclass
class ProcessingParams:
    contrast: float = 2.0
    brightness: float = 1.0
    sharpness: float = 1.0
    threshold: int = 128
    blur: int = 0
    dilate: int = 1
    erode: int = 1
    gamma: float = 1.0
    adaptive_thresh: bool = False
    invert: bool = False
    denoise: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'contrast': self.contrast,
            'brightness': self.brightness,
            'sharpness': self.sharpness,
            'threshold': self.threshold,
            'blur': self.blur,
            'dilate': self.dilate,
            'erode': self.erode,
            'gamma': self.gamma,
            'adaptive_thresh': self.adaptive_thresh,
            'invert': self.invert,
            'denoise': self.denoise
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class CameraConfig:
    index: int = 1
    rtsp_url: str = ""
    username: str = ""
    password: str = ""
    use_rtsp: bool = False

@dataclass
class OCRConfig:
    language: str = "tur"
    selection_rect: QRect = field(default_factory=lambda: QRect(100, 100, 200, 150))

@dataclass
class DatabaseConfig:
    server: str = "localhost"
    database: str = "SensorDB"
    username: str = "sa"
    password: str = ""
    use_windows_auth: bool = False
    is_remote: bool = False
    port: int = 1433
    connection_string: str = ""

@dataclass
class SensorData:
    temperature: float = 0.0
    humidity: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None

@dataclass
class OCRSensorData:
    raw_text: str = ""
    temperature: Optional[float] = None
    is_valid: bool = False
    
    def parse_temperature_from_text(self, text: str) -> bool:
        """OCR metninden sadece sıcaklık değerini çıkar"""
        self.raw_text = text.strip()
        self.temperature = None
        self.is_valid = False
        
        if not text:
            return False
        
        # Çeşitli sıcaklık formatları için regex pattern'leri
        patterns = [
            r'(\d+\.?\d*)\s*°?[Cc]',  # "25.5°C" formatı
            r'[Ss]ıcaklık\s*[:=]?\s*(\d+\.?\d*)',  # "Sıcaklık: 25.5" formatı
            r'[Tt]emp\s*[:=]?\s*(\d+\.?\d*)',  # "Temp: 25.5" formatı
            r'(\d+\.?\d*)',  # Sadece sayı "25.5" formatı
            r'(\d+,\d*)'  # "25,5" (virgüllü) formatı
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    # Virgüllü sayıları noktaya çevir
                    temp_str = match.group(1).replace(',', '.')
                    temp = float(temp_str)
                    
                    # Sıcaklık değerinin mantıklı aralıkta olduğunu kontrol et
                    if -50 <= temp <= 150:
                        self.temperature = temp
                        self.is_valid = True
                        return True
                except (ValueError, IndexError, AttributeError):
                    continue
        
        return False