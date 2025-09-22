# Infrastructure/WebService.py
import requests
import json
from Domain.Models import SensorData

class WebService:
    def __init__(self):
        pass

    def send_sensor_data(self, data: SensorData, url: str) -> tuple[bool, str]:
        """Sıcaklık ve nem verilerini bir web servisine POST isteği olarak gönderir."""
        if not url:
            return False, "Hata: Web Servis URL'si boş bırakılamaz."
        
        # Gönderilecek veriyi JSON formatına dönüştür
        payload = {
            "temperature": data.temperature,
            "humidity": data.humidity,
            "timestamp": data.timestamp.isoformat()  # Zaman damgasını ISO formatına dönüştür
        }
        
        try:
            headers = {"Content-Type": "application/json"}
            # POST isteği gönder
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
            response.raise_for_status()  # HTTP hatalarını kontrol et (örn. 404, 500)
            
            # Başarılı yanıt
            return True, f"Veri başarıyla gönderildi. Sunucu yanıtı: {response.text}"
            
        except requests.exceptions.RequestException as e:
            # Bağlantı hatalarını veya diğer istek hatalarını yakala
            return False, f"Web Servis bağlantı hatası: {e}"
        except Exception as e:
            return False, f"Genel hata: {e}"