import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QRect
from Domain.Models import CameraConfig

class CameraService(QObject):
    frame_updated = pyqtSignal(np.ndarray)
    camera_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.current_frame = None
        self.config = CameraConfig()
        self.is_running = False
        
    def get_available_cameras(self):
        cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(f"Kamera {i}")
                cap.release()
        return cameras
        
    def start_camera(self, config: CameraConfig):
        self.config = config
        
        if self.cap is not None:
            self.cap.release()
            
        if config.use_rtsp:
            rtsp_url = config.rtsp_url.strip()
            username = config.username.strip()
            password = config.password.strip()
            
            if not rtsp_url:
                self.camera_error.emit("Lütfen RTSP URL girin!")
                return False
                
            if username and password:
                if "://" in rtsp_url:
                    protocol, rest = rtsp_url.split("://", 1)
                    rtsp_url = f"{protocol}://{username}:{password}@{rest}"
                else:
                    rtsp_url = f"{username}:{password}@{rtsp_url}"
            
            self.cap = cv2.VideoCapture(rtsp_url)
            
        else:
            self.cap = cv2.VideoCapture(config.index)
        
        if not self.cap.isOpened():
            self.camera_error.emit("Kamera açılamadı! Bağlantıyı kontrol edin.")
            return False
            
        self.is_running = True
        return True
        
    def stop_camera(self):
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
    def read_frame(self):
        if self.cap is not None and self.is_running:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.frame_updated.emit(frame)
                return frame
            else:
                self.camera_error.emit("Görüntü alınamıyor. Bağlantıyı kontrol edin.")
        return None
        
    def get_frame(self):
        return self.current_frame